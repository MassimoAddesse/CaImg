import numpy as np 
import pandas as pd

from detection.base import DetectionResult
from metrics.event_analysis import EventAnalysis

def profile_all_cells(
        dff_df: pd.DataFrame,
        detection_results: dict[str, DetectionResult],
        sampling_rate: float
) -> dict[str, list[EventAnalysis]]:

    """
    Calculate event-based metrics for all detected events.

    Each ROI is processed independently. For every detected
    event, a EventAnalysis object is created and all event-level 
    metrics are calculated.

    Parameters
    ----------
    dff_df : pandas.DataFrame
        DFF dataframe where each column represents one ROI. 
    detection_results : dict[str, DetectionResults]
        Dictionary containing the detection results for each ROI.
        The ROI identified is used as the dictionary key.
    sampling_rate : float
        Sampling rate of the recording in Hz.
    
    Returns
    -------
    dict[str, list [EventAnalysis]]
        Dictionary containing the EventAnalysis objects for each ROI.

        Each key corresponds to one ROI and its value is a list
        containing all the detected events for that cell.
    """

    if sampling_rate <= 0:
        raise ValueError(
            "sampling_rate must be greater than zero"
        )
    
    profiles = {}

    for roi, results in detection_results.items():
        if roi not in dff_df.columns:
            raise KeyError(
                f"ROI '{roi}' was found in detection results "
                "but not in the DFF dataframe"
            )

        profiles[roi] = []
        
        dff = dff_df[roi].to_numpy(
            dtype = float
        )

        events = sorted(
            results.events,
            key = lambda event: event.onset
        )

        for event in events: 

            profiler = EventAnalysis(
                event = event,
                dff = dff,
                sampling_rate = sampling_rate
            )

            profiler.calculate()

            profiles[roi].append(profiler)

    return profiles
