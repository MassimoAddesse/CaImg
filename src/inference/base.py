from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np

@dataclass
class InferenceResult:
    roi: str
    spike_activity: np.ndarray
    denoised_calcium: np.ndarray | None = None
    baseline: np.ndarray | None = None
    spike_events: np.ndarray | None = None
    sampling_rate: float = 4.0

class Inference(ABC):
    @abstractmethod
    def infer(
        self,
        dff: np.ndarray,
        roi: str
    ) -> InferenceResult:
        raise NotImplementedError