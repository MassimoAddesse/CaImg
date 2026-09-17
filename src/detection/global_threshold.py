import numpy as np
from scipy.signal import find_peaks
from .base import EventDetector, DetectionResult
from .hysteresis import find_hysteresis_boundaries

class GlobalThresholdDetector(EventDetector):

    def __init__(
            self,
            threshold: float,
            low_threshold: float | None = None,
            min_event_duration: int = 2,
            min_peak_distance: int = 5
    ):

        self.threshold = threshold

        if low_threshold is None:
            low_threshold = threshold

        self.low_threshold = low_threshold

        self.min_event_duration = (
            min_event_duration
        )

        self.min_peak_distance = (
            min_peak_distance
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

        threshold_high = np.full(
            dff.shape,
            self.threshold,
            dtype = float
        )

        threshold_low = np.full(
            dff.shape,
            self.low_threshold,
            dtype = float
        )

        candidate_signal = np.where(
            np.isfinite(dff)
            & (dff > self.threshold),
            dff,
            -np.inf
        )

        peaks, _ = find_peaks(
            candidate_signal,
            distance = self.min_peak_distance
        )

        onsets, offsets = find_hysteresis_boundaries(
            signal = dff,
            peak_indices = peaks,
            threshold_low = threshold_low
        )

        duration = offsets - onsets + 1

        keep = (
            duration
            >= self.min_event_duration
        )

        peaks = peaks[keep]
        onsets = onsets[keep]
        offsets = offsets[keep]

        return DetectionResult(
            peak_indices=peaks,
            onset_indices=onsets,
            offset_indices=offsets,
            detection_signal=dff,
            threshold_high=threshold_high,
            threshold_low=threshold_low
        )
        