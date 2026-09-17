import numpy as np
from scipy.signal import find_peaks
from .base import EventDetector, DetectionResult, DetectionEvent
from .hysteresis import find_hysteresis_boundaries 

class AdaptiveSTDDetector(EventDetector):

    def __init__(self, config):
        self.config = config

    def _estimate_baseline_noise(
        self, 
        dff: np.ndarray
    ) -> tuple[float, float, np.ndarray]:
        """
        Estimate baseline mean and robust STD.

        A preliminary detection is performed first. Frames
        belonging to preliminary events are excluded from the noise estimation.
        """

        valid = np.isfinite(dff)
        if not np.any(valid):
            raise ValueError(
                "DFF trace contains no valid values"
            )

        initial_values = dff[valid]

        median = np.median(initial_values)

        initial_deviation = np.abs(
            initial_values - median
        )

        initial_mad = np.median(
            initial_deviation
        )

        robust_sigma = 1.4826 * initial_mad

        if robust_sigma <= 0:
            robust_sigma = np.std(initial_values)

        if robust_sigma <= 0:
            raise ValueError(
                f"Unable to estimate noise from DFF trace. "
                f"Valid values: {initial_values.size}, "
                f"min: {np.min(initial_values)}, "
                f"max: {np.max(initial_values)}, "
                f"STD: {np.std(initial_values)}"
            )

        preliminary_threshold = (
            median + 2.0 * robust_sigma
        )

        candidate_mask = (
            np.isfinite(dff)
            & (dff > preliminary_threshold)
        )

        baseline_values = dff[
            valid & ~candidate_mask
        ]

        if baseline_values.size < 2:

            baseline_values = initial_values

        baseline_mean = np.mean(
            baseline_values
        )

        baseline_std = np.std(
            baseline_values,
            ddof = 1
        )

        if baseline_std <= 0:
            raise ValueError(
                "Baseline STD is zero"
            )

        return (
            baseline_mean,
            baseline_std,
            candidate_mask
        )

    def detect(
            self,
            dff: np.ndarray,
            roi: str
    ) -> DetectionResult:

        dff = np.asarray(
            dff,
            dtype = float
        )

        if dff.ndim != 1:
            raise ValueError(
                "dff must be one-dimensional"
            )

        baseline_mean, baseline_std, _ = (
            self._estimate_baseline_noise(dff)
        )

        threshold_high_value = (
            baseline_mean
            + self.config.std_k_high * baseline_std
        )

        threshold_low_value = (
            baseline_mean
            + self.config.std_k_low * baseline_std
        )

        threshold_high = np.full(
            dff.shape,
            threshold_high_value,
            dtype = float
        )

        threshold_low = np.full(
            dff.shape,
            threshold_low_value,
            dtype = float
        )

        valid = np.isfinite(dff)

        candidate_signal = np.where(
            valid & (dff > threshold_high),
            dff,
            -np.inf
        )

        peaks, _ = find_peaks(
            candidate_signal,
            distance = self.config.min_peak_distance
        )

        onsets, offsets = find_hysteresis_boundaries(
            signal = dff,
            peak_indices = peaks,
            threshold_low = threshold_low
        )

        duration = offsets - onsets + 1

        keep = (
            duration
            >= self.config.min_event_duration
        )

        peaks = peaks[keep]
        onsets = onsets[keep]
        offsets = offsets[keep]
        
        events = []

        for event_id, (onset, peak, offset) in enumerate(
            zip(onsets, peaks, offsets),
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
            detection_signal=dff,
            threshold_high=threshold_high,
            threshold_low=threshold_low
        )
        
    

    

