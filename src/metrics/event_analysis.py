import numpy as np
from detection.base import DetectionEvent
from .event_metrics import(
    calculate_amplitude,
    calculate_auc,
    calculate_duration,
    calculate_rise_time,
    calculate_decay_time,
    calculate_rise_speed,
    calculate_decay_speed,
    calculate_rise_time_10_90,
    calculate_decay_time_10_90,
    calculate_rise_speed_10_90,
    calculate_decay_speed_10_90,
    calculate_fwhm
)

class EventAnalysis:
    """
    Event-based profiler for calcium imaging data

    EventAnalysis object represents one detected calcium event belonging to one ROI.

    Parameters
    ----------

    event: Detection Event
        Detected calcium event to be quantified

    dff : np.ndarray
        Original DFF trace of the ROI.
    
    sampling_rate : float
        Sampling rate of the recording in Hz

    Returns
    -------
    EventAnalysis
        Event-based profiler containing all calculated metrics for the event
    """


    def __init__(
        self,
        event: DetectionEvent,
        dff: np.ndarray,
        sampling_rate: float
    ):

        self.event = event
        self.dff = np.asarray(
            dff,
            dtype = float
        )

        self.sampling_rate = sampling_rate

        self.amplitude = None
        self.auc = None
        self.duration = None

        self.rise_time = None
        self.decay_time = None

        self.rise_speed = None
        self.decay_speed = None

        self.rise_time_10_90 = None
        self.decay_time_10_90 = None

        self.rise_speed_10_90 = None
        self.decay_speed_10_90 = None

        self.fwhm = None

    def calculate(self):
        """
        Calculate all event-level metrics.

        Returns
        -------
        EventAnalysis
            Current object containing all 
            calculated event metrics.
        """

        self.amplitude = calculate_amplitude(
            self.event,
            self.dff
        )

        self.auc = calculate_auc(
            self.event,
            self.dff,
            self.sampling_rate
        )

        self.duration = calculate_duration(
            self.event,
            self.sampling_rate
        )

        self.rise_time = calculate_rise_time(
            self.event,
            self.sampling_rate
        )

        self.decay_time = calculate_decay_time(
            self.event,
            self.sampling_rate
        )

        self.rise_speed = calculate_rise_speed(
            self.event,
            self.dff,
            self.sampling_rate
        )

        self.decay_speed = calculate_decay_speed(
            self.event,
            self.dff,
            self.sampling_rate
        )

        self.rise_time_10_90 = calculate_rise_time_10_90(
            self.event,
            self.dff,
            self.sampling_rate
        )

        self.decay_time_90_10 = calculate_decay_time_10_90(
            self.event,
            self.dff,
            self.sampling_rate
        )

        self.rise_speed_10_90 = calculate_rise_speed_10_90(
            self.event,
            self.dff,
            self.sampling_rate
        )

        self.decay_speed_90_10 = calculate_decay_speed_10_90(
            self.event,
            self.dff,
            self.sampling_rate
        )

        self.fwhm = calculate_fwhm(
            self.event,
            self.dff,
            self.sampling_rate
        )

        return self

    def to_dict(self) -> dict:
        """
        Convert the EventAnalysis object into a dictionary.

        The dictionary contains the event identifiers,
        temporal boundaries, and all calculated metrics.

        Returns
        -------
        dict
            Dictionary containing all event-level results.
        """

        return {
            "ROI": self.event.roi,
            "Event": self.event.event_id,

            "Onset": self.event.onset,
            "Peak": self.event.peak,
            "Offset": self.event.offset,

            "Amplitude": self.amplitude,
            "AUC": self.auc,

            "Duration": self.duration,

            "Rise_Time": self.rise_time,
            "Decay_Time": self.decay_time,

            "Rise_Speed": self.rise_speed,
            "Decay_Speed": self.decay_speed,

            "Rise_Time_10_90": self.rise_time_10_90,
            "Decay_Time_90_10": self.decay_time_90_10,

            "Rise_Speed_10_90": self.rise_speed_10_90,
            "Decay_Speed_90_10": self.decay_speed_90_10,

            "FWHM": self.fwhm,
        }
