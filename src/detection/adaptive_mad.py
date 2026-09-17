import numpy as np
from scipy.signal import find_peaks
from .base import EventDetector, DetectionResult
from .hysteresis import find_hysteresis_boundaries

class AdaptiveMADDetector(EventDetector):

    def __init__(self, config):
        self.config = config

    def _estimate_baseline(
            self,
            dff: np.ndarray
    ) -> tuple[float, float]:

        valid_values = dff[
            np.isfinite(dff)
        ]

        if valid_values.size == 0: 
            raise ValueError(
                "DFF trace contains no valid values"
            )

        median = np.median(
            valid_values
        )

        mad = np.median(
            np.abs(
                valid_values - median
            )
        )

        sigma = 1.4826 * mad

        if sigma <= 0:
            sigma = np.std(
                valid_values
            )

        if sigma <= 0:
            raise ValueError(
                "Unable to estimate noise"
            )

        preliminary_threshold = (
            median + 2.0 * sigma
        )

        baseline_values = valid_values[
            valid_values <= preliminary_threshold
        ]

        if baseline_values.size < 2:
            baseline_values = valid_values

        baseline_median = np.median(
            baseline_values
        )

        baseline_mad = np.median(
            np.abs(
                baseline_values
                - baseline_median
            )
        )

        robust_sigma = (
            1.4826 * baseline_mad
        )

        if robust_sigma <= 0:
            robust_sigma = np.std(
                baseline_values
            )

        if robust_sigma <= 0:
            raise ValueError(
                "Baseline noise estimate is zero"
            )

        return (
            baseline_median,
            robust_sigma
        )

    def detect(
            self,
            dff: np.ndarray
    ) -> DetectionResult:

        dff = np.asarray(
            dff,
            dtype = float
        )

        if dff.ndim != 1:
            raise ValueError(
                "dff must be one-dimensional"
            )

        baseline, robust_sigma = (
            self._estimate_baseline(dff)
        )

        threshold_high_value = (
            baseline
            + self.config.mad_k_high
            * robust_sigma
        )

        threshold_low_value = (
            baseline
            + self.config.mad_k_low
            * robust_sigma
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

        candidate_signal = np.where(
            np.isfinite(dff)
            & (dff > threshold_high),
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
        onsets = peaks[keep]
        offsets = offsets[keep]

        return DetectionResult(
            peak_indices=peaks,
            onset_indices=onsets,
            offset_indices=offsets,
            detection_signal=dff,
            threshold_high=threshold_high,
            threshold_low=threshold_low
        )