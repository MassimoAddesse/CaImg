import pandas as pd

from .cell_metrics import calculate_cell_metrics
from .coactivity import (
    build_activity_matrix,
    calculate_population_activity,
    calculate_pairwise_coactivity,
    calculate_event_overlap,
)
from .synchrony import calculate_event_synchrony
from .correlation import (
    calculate_pearson_correlation,
    calculate_spearman_correlation,
)


def run_analysis(
    dff_df: pd.DataFrame,
    profiles: dict,
    recording_duration: float,
    sampling_rate: float,
    synchrony_tolerance_frames: int = 3,
) -> dict:

    """
    Run all cell-level and population-level analyses.

    Parameters
    ----------
    dff_df : pandas.DataFrame
        DFF dataframe where each column represents one ROI and
        each row represents one frame.

    profiles : dict
        Dictionary containing EventAnalysis objects for each ROI.

    recording_duration : float
        Total duration of the recording in seconds.

    sampling_rate : float
        Sampling rate of the recording in Hz.

    synchrony_tolerance_frames : int, optional
        Maximum difference in event onset frames for two events
        to be considered synchronous.

    Returns
    -------
    dict
        Dictionary containing the results of all analysis modules.
    """

    if dff_df.empty:
        raise ValueError("dff_df cannot be empty.")

    if sampling_rate <= 0:
        raise ValueError("sampling_rate must be greater than zero.")

    if recording_duration < 0:
        raise ValueError("recording_duration must be non-negative.")

    if synchrony_tolerance_frames < 0:
        raise ValueError(
            "synchrony_tolerance_frames must be non-negative."
        )

    cell_metrics = calculate_cell_metrics(
        profiles=profiles,
        recording_duration=recording_duration,
        sampling_rate=sampling_rate,
    )

    activity_matrix = build_activity_matrix(
        profiles=profiles,
        n_frames=len(dff_df),
    )

    population_activity = calculate_population_activity(
        activity_matrix
    )

    pairwise_coactivity = calculate_pairwise_coactivity(
        activity_matrix
    )

    event_overlap = calculate_event_overlap(
        profiles
    )

    event_synchrony = calculate_event_synchrony(
        profiles=profiles,
        tolerance_frames=synchrony_tolerance_frames,
    )

    pearson_correlation = calculate_pearson_correlation(
        dff_df
    )

    spearman_correlation = calculate_spearman_correlation(
        dff_df
    )

    return {
        "cell_metrics": cell_metrics,
        "activity_matrix": activity_matrix,
        "population_activity": population_activity,
        "pairwise_coactivity": pairwise_coactivity,
        "event_overlap": event_overlap,
        "event_synchrony": event_synchrony,
        "pearson_correlation": pearson_correlation,
        "spearman_correlation": spearman_correlation,
    }

