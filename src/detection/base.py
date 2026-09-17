from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass
class DetectionEvent:
    """
    Store one detected calcium event belonging to one ROI.

    Parameters
    ----------
    roi : str
        Identifier of the ROI/cell.

    event_id : int
        Sequential identifier of the event within the ROI.

    onset : int
        Frame index corresponding to the event onset.

    peak : int
        Frame index corresponding to the event peak.

    offset : int
        Frame index corresponding to the event offset.

    Returns
    -------
    DetectionEvent
        Dataclass containing the temporal information of
        one detected calcium event.
    """
    roi: str
    event_id: int

    onset: int
    peak: int
    offset: int


@dataclass
class DetectionResult:
    """
    Store all detected events belonging to one ROI.

    Parameters
    ----------
    events : list[DetectionEvent]
        Chronologically ordered list of detected events.

    detection_signal : np.ndarray or None, optional
        Signal used by the detector for event identification.
        This may be a filtered version of the original DFF.

    threshold_high : np.ndarray or None, optional
        Upper detection threshold, if used by the detection
        method.

    threshold_low : np.ndarray or None, optional
        Lower detection threshold, if used by the detection
        method.

    Returns
    -------
    DetectionResult
        Dataclass containing all detection information for
        one ROI.
    """
    
    events: list[DetectionEvent]

    detection_signal: np.ndarray | None = None

    threshold_high: np.ndarray | None = None
    threshold_low: np.ndarray | None = None


class EventDetector(ABC):
    """
    Abstract base class for calcium event detectors.

    Every detection method implemented in CaImg Analyzer
    should inherit from this class and implement the
    `detect` method.
    """

    @abstractmethod
    def detect(
        self,
        dff: np.ndarray,
        roi: str
    ) -> DetectionResult:
        """
        Detect calcium events in one ROI.

        Parameters
        ----------
        dff : np.ndarray
            DFF trace of a single ROI.

        roi : str
            Identifier of the ROI/cell.

        Returns
        -------
        DetectionResult
            Detection results containing the events detected
            in the ROI.
        """

        raise NotImplementedError
