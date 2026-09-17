from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.signal import find_peaks
from .base import InferenceResult, SpikeInference

@dataclass
class OasisConfig:
    sampling_rate: float = 4.0
    tau_d: float | None = None
    tau_r: float | None = None
    penalty: float = 1.0
    spike_prominence: float = 0.0
    min_spike_distance: int = 2
    allow_nan: bool = True

class OasisInference(SpikeInference):
    def __init__(
            self,
            config: OasisConfig
    ):
        self.config = config

    def infer(
            self,
            dff: np.ndarray,
            roi: str
    ) -> InferenceResult:

        try:
            from oasis.functions import deconvolve
        except ImportError as exc:
            raise ImportError(
                "Oasis is not installed. Run: pip install oasis-deconv"
            ) from exc

        y = np.asarray(dff, dtype = float)

        if y.ndim != 1:
            raise ValueError(f"{roi}: DFF trace must be 1D.")
        if y.size < 5:
            raise ValueError(f"{roi}: DFF trace is too short.")
        finite = np.isfinite(y)
        if not np.any(finite):
            raise ValueError(f"{roi}: no finite DFF values.")

        if not self.config.allow_nan and not np.all(finite):
            raise ValueError(f"{roi}: DFF contains NaNs.")

        kwargs = {
            "penalty" : float(self.config.penalty),
            "framerate": float(self.config.sampling_rate)
        }

        if self.config.tau_d is not None:
            kwargs["tau_d"] = float(self.config.tau_d)
        if self.config.tau_r is not None:
            kwargs["tau_r"] = float(self.config.tau_r)

        result = deconvolve(y, **kwargs)

        calcium = np.asarray(result.c, dtype = float)
        acivity = np.asarray(result.s, dtype = float)
        baseline = np.asarray(result.b, dtype = float)

        clean_activity = np.where(np.isfinite(activity), acivity, 0.0)
        peaks, _ = find_peaks(
            clean_activity,
            prominence = float(self.config.spike_prominence),
            distance = max(1, int(self.config.min_spike_distance))
        )

        if self.config.allow_nan:
            peaks = peaks[finite[peaks]]

        return InferenceResult(
            roi = roi,
            spike_activity = acivity,
            denoised_calcium = calcium,
            baseline = baseline,
            spike_events = peaks.astype(int),
            sampling_rate = float(self.config.sampling_rate)
        )