import numpy as np
from scipy.signal import find_peaks, savgol_filter

from .base import (
    EventDetector,
    DetectionResult,
    DetectionEvent
)

class SGProminenceDetector(EventDetector):

    def __init__(self, config):
        self.config = config

    def _validate_window(
            self,
            signal_length: int
    ) -> int:
        """
        Validate the Savitzky-Golay filter parameters.

        Parameters
        ----------
        signal_length : int
            Number of samples in the signal.

        Returns
        -------
        int
            Validated Savitzky-Golay window length.
        """

        window = self.config.sg_window

        if window <= 0:
            raise ValueError(
                "sg_window must be greater than zero."
            )

        if window % 2 == 0:
            raise ValueError(
                "sg_window must be odd."
            )

        if window >= signal_length:
            raise ValueError(
                "sg_window must be smaller than "
                "the signal length."
            )

        if self.config.sg_polyorder >= window:
            raise ValueError(
                "sg_polyorder must be smaller than "
                "sg_window."
            )

        return window

    def _filter_valid_segments(
            self,
            dff: np.ndarray,
            window: int
    ) -> np.ndarray:
        """
        Apply Savitzky-Golay filtering only to valid DFF segments.

        NaN values are preserved and are not included in the filtering.
        This allows the detector to handle the NaNs generated at the
        edges of the DFF calculation.

        Parameters
        ----------
        dff : np.ndarray
            DFF trace containing finite values and possibly NaNs.

        window : int
            Savitzky-Golay filter window length.

        Returns
        -------
        np.ndarray
            Filtered DFF trace with NaN values preserved.
        """

        filtered = np.full(
            dff.shape,
            np.nan,
            dtype=float
        )

        valid = np.isfinite(dff)

        if not np.any(valid):
            raise ValueError(
                "DFF trace contains no valid values."
            )

        valid_indices = np.flatnonzero(valid)

        segment_start = valid_indices[0]
        previous_index = valid_indices[0]

        segments = []

        for index in valid_indices[1:]:

            if index != previous_index + 1:

                segments.append(
                    (
                        segment_start,
                        previous_index + 1
                    )
                )

                segment_start = index

            previous_index = index

        segments.append(
            (
                segment_start,
                previous_index + 1
            )
        )

        for start, end in segments:

            segment = dff[start:end]

            if len(segment) < window:
                continue

            filtered[start:end] = savgol_filter(
                segment,
                window_length=window,
                polyorder=self.config.sg_polyorder
            )

        return filtered

    def detect(
            self,
            dff: np.ndarray,
            roi: str
    ) -> DetectionResult:
        """
        Detect calcium events using Savitzky-Golay filtering
        and peak prominence.

        Parameters
        ----------
        dff : np.ndarray
            DFF trace of a single ROI.

        roi : str
            Identifier of the ROI/cell.

        Returns
        -------
        DetectionResult
            Detection results containing the detected calcium
            events and the filtered signal.
        """

        dff = np.asarray(
            dff,
            dtype=float
        )

        if dff.ndim != 1:
            raise ValueError(
                "dff must be one-dimensional."
            )

        valid = np.isfinite(dff)

        if not np.any(valid):
            raise ValueError(
                "DFF trace contains no valid values."
            )

        valid_values = dff[valid]

        window = self._validate_window(
            len(valid_values)
        )

        filtered = self._filter_valid_segments(
            dff,
            window
        )

        valid_filtered = np.isfinite(filtered)

        if not np.any(valid_filtered):
            raise ValueError(
                "Unable to apply SG filtering to the valid "
                "DFF signal."
            )

        residual = (
            dff[valid_filtered]
            - filtered[valid_filtered]
        )

        median_residual = np.median(
            residual
        )

        mad_residual = np.median(
            np.abs(
                residual
                - median_residual
            )
        )

        noise_sigma = (
            1.4826
            * mad_residual
        )

        if noise_sigma <= 0:
            noise_sigma = np.std(
                residual,
                ddof=1
            )

        if noise_sigma <= 0:
            raise ValueError(
                "Unable to estimate noise for "
                "SG + prominence."
            )

        prominence = (
            self.config.prominence_k
            * noise_sigma
        )
        
        peaks_list = []

        filtered_indices = np.flatnonzero(
            valid_filtered
        )

        segment_start = filtered_indices[0]
        previous_index = filtered_indices[0]

        segments = []

        for index in filtered_indices[1:]:

            if index != previous_index + 1:

                segments.append(
                    (
                        segment_start,
                        previous_index + 1
                    )
                )

                segment_start = index

            previous_index = index

        segments.append(
            (
                segment_start,
                previous_index + 1
            )
        )

        for start, end in segments:

            segment = filtered[start:end]

            if len(segment) < 2:
                continue

            local_peaks, _ = find_peaks(
                segment,
                prominence=prominence,
                distance=self.config.min_peak_distance
            )

            peaks_list.extend(
                (
                    local_peak + start
                    for local_peak in local_peaks
                )
            )

        peaks = np.asarray(
            peaks_list,
            dtype=int
        )

        filtered_valid_values = filtered[
            valid_filtered
        ]

        threshold_low = (
            np.median(
                filtered_valid_values
            )
            + self.config.mad_k_low
            * noise_sigma
        )

        threshold_low_array = np.full(
            filtered.shape,
            np.nan,
            dtype=float
        )

        threshold_low_array[
            valid_filtered
        ] = threshold_low

        onsets = []
        offsets = []

        for peak in peaks:

            onset = peak

            while onset > 0:

                previous_value = filtered[
                    onset - 1
                ]

                if (
                    not np.isfinite(previous_value)
                    or previous_value < threshold_low
                ):
                    break

                onset -= 1

            offset = peak

            while offset < len(filtered) - 1:

                next_value = filtered[
                    offset + 1
                ]

                if (
                    not np.isfinite(next_value)
                    or next_value < threshold_low
                ):
                    break

                offset += 1

            onsets.append(onset)
            offsets.append(offset)

        onsets = np.asarray(
            onsets,
            dtype=int
        )

        offsets = np.asarray(
            offsets,
            dtype=int
        )

        if len(peaks) > 0:

            duration = (
                offsets
                - onsets
                + 1
            )

            keep = (
                duration
                >= self.config.min_event_duration
            )

            peaks = peaks[keep]
            onsets = onsets[keep]
            offsets = offsets[keep]

        events = []

        for event_id, (
            onset,
            peak,
            offset
        ) in enumerate(
            zip(
                onsets,
                peaks,
                offsets
            ),
            start=1
        ):

            events.append(
                DetectionEvent(
                    roi=roi,
                    event_id=event_id,
                    onset=int(onset),
                    peak=int(peak),
                    offset=int(offset)
                )
            )
            
        return DetectionResult(
            events=events,
            detection_signal=filtered,
            threshold_high=None,
            threshold_low=threshold_low_array
        )
