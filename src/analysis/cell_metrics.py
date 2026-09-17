import numpy as np
import pandas as pd

from metrics.event_analysis import EventAnalysis

def calculate_cell_metrics(
        profiles: dict[str,list[EventAnalysis]],
        recording_duration: float,
        sampling_rate: float
) -> pd.DataFrame:

    """
    Calculate cell-level metrics from event-based profiles.

    Event-level metrics calculated by EventAnalysis are grouped by ROI
    and summarized using mean and median.

    Parameters
    ----------
    profiles : dict[str, list[EventAnalysis]]
        Dictionary containing EventAnalysis objects for each ROI. 
        The ROI identifier is used as the dictionary key.

    recording_duration : float
        Total recording duration in seconds

    sampling_rate : float
        Sampling rate in Hz, used to convert frame-based event onsets
        into seconds when calculating inter-event intervals. 

    Returns
    -------
    pandas.DataFrame
        DataFrame containing one row for every ROI and columns
        containing cell-level activity metrics.
    """

    if recording_duration < 0:
        raise ValueError("recording duration must be non-negative")

    if sampling_rate <= 0:
        raise ValueError("samplig rate must be greater than zero")

    cell_profiles = []

    for roi, events in profiles.items():
        n_events = len(events)

        if n_events == 0:
            cell_profiles.append(
                {
                    "ROI" : roi,
                    "n_events" : 0,
                    "event_frequency" : 0.0,
                    "mean_amplitude" : np.nan,
                    "median_amplitude" : np.nan,
                    "mean_auc" : np.nan,
                    "median_auc" : np.nan,
                    "mean_duration" : np.nan,
                    "median_duration" : np.nan,
                    "mean_rise_time" : np.nan,
                    "median_rise_time" : np.nan,
                    "mean_decay_time" : np.nan,
                    "median_decay_time" : np.nan,
                    "mean_rise_speed" : np.nan,
                    "median_rise_speed" : np.nan,
                    "mean_decay_speed" : np.nan,
                    "median_decay_speed" : np.nan,
                    "mean_rise_time_10_90": np.nan,
                    "median_rise_time_10_90": np.nan,
                    "mean_decay_time_10_90": np.nan,
                    "median_decay_time_10_90": np.nan,
                    "mean_rise_speed_10_90": np.nan,
                    "median_rise_speed_10_90": np.nan,
                    "mean_decay_speed_10_90": np.nan,
                    "median_decay_speed_10_90": np.nan,
                    "mean_fwhm": np.nan,
                    "median_fwhm": np.nan,
                    "mean_iei" : np.nan,
                    "median_iei" : np.nan
                }
            )

            continue
        
        amplitudes = np.array(
            [event.amplitude for event in events],
            dtype = float
        )

        aucs = np.array(
            [event.auc  for event in events],
            dtype = float
        )

        durations = np.array(
                    [event.duration  for event in events],
                    dtype = float
                )

        rise_times = np.array(
                    [event.rise_time  for event in events],
                    dtype = float
                )

        decay_times = np.array(
                    [event.decay_time  for event in events],
                    dtype = float
                )

        rise_speeds = np.array(
                    [event.rise_speed  for event in events],
                    dtype = float
                )

        decay_speeds = np.array(
                    [event.decay_speed  for event in events],
                    dtype = float
                )
        
        rise_times_10_90 = np.array(
                    [event.rise_time_10_90 for event in events],
                    dtype=float
                )
        
        decay_times_10_90 = np.array(
                    [event.decay_time_10_90 for event in events],
                    dtype=float
                )
        
        rise_speeds_10_90 = np.array(
                    [event.rise_speed_10_90 for event in events], 
                    dtype=float
                )
        
        decay_speeds_10_90 = np.array(
                    [event.decay_speed_10_90 for event in events], 
                    dtype=float
                )
        
        fwhms = np.array(
                    [event.fwhm for event in events], 
                    dtype=float
                )

        onsets = np.array(
                    [event.event.onset  for event in events],
                    dtype = float
                )

        if len(onsets) > 1:
            iei_seconds = np.diff(onsets) / sampling_rate
            mean_iei = np.mean(iei_seconds)
            median_iei = np.median(iei_seconds)
        else:
            mean_iei = np.nan
            median_iei = np.nan

        event_frequency = (
            n_events / recording_duration
            if recording_duration > 0
            else np.nan
        )

        cell_profiles.append(
            {
                "ROI" : roi,
                "n_events" : n_events,
                "event_frequency" : event_frequency,
                "mean_amplitude" : np.mean(amplitudes),
                "median_amplitude" : np.median(amplitudes),
                "mean_auc" : np.mean(aucs),
                "median_auc" : np.median(aucs),
                "mean_duration" : np.mean(durations),
                "median_duration" : np.median(durations),
                "mean_rise_time" : np.mean(rise_times),
                "median_rise_time" : np.median(rise_times),
                "mean_decay_time" : np.mean(decay_times),
                "median_decay_time" : np.median(decay_times),
                "mean_rise_speed" : np.mean(rise_speeds),
                "median_rise_speed" : np.median(rise_speeds),
                "mean_decay_speed" : np.mean(decay_speeds),
                "median_decay_speed" : np.median(decay_speeds),
                "mean_rise_time_10_90": np.mean(rise_times_10_90),
                "median_rise_time_10_90": np.median(rise_times_10_90),
                "mean_decay_time_10_90": np.mean(decay_times_10_90),
                "median_decay_time_10_90": np.median(decay_times_10_90),
                "mean_rise_speed_10_90": np.mean(rise_speeds_10_90),
                "median_rise_speed_10_90": np.median(rise_speeds_10_90),
                "mean_decay_speed_10_90": np.mean(decay_speeds_10_90),
                "median_decay_speed_10_90": np.median(decay_speeds_10_90),
                "mean_fwhm": np.mean(fwhms),
                "median_fwhm": np.median(fwhms),
                "mean_iei" : mean_iei,
                "median_iei" : median_iei
            }
        )

    return pd.DataFrame(cell_profiles)
