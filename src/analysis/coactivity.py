import numpy as np
import pandas as pd

from metrics.event_analysis import EventAnalysis

def build_activity_matrix(
        profiles: dict[str, list[EventAnalysis]],
        n_frames: int,
) -> pd.DataFrame:
    """
    Build a binary cell-activity matrix from detected calcium events.

    A cell is considered active between the onset and offset of each
    detected event. The resulting matrix contains one row per frame
    and one column per ROI.

    Parameters
    ----------
    profiles : dict[str, list[EventAnalysis]]
        Dictionary containing the EventAnalysis objects for each ROI.
        The ROI identified is used as the dictionary key

    n_frames : int
        Number of frames in the original recording.
    
    Returns
    -------
    pandas.DataFrame
        Binary activity matrix.
        Rows correspond to frames.
        Columns correspond to ROIs.
        Bool-indicator for cell activity 
    """

    if n_frames <= 0:
        raise ValueError(
            "n_frames must be greater than zero"
        )

    rois = list(profiles.keys())

    activity = np.zeros(
        (n_frames, len(rois)),
        dtype = int
    )

    for roi_index, roi in enumerate(rois):

        for profiler in profiles[roi]:

            onset = max(
                0,
                int(profiler.event.onset)
            )

            offset = min(
                n_frames - 1,
                int(profiler.event.offset)
            )

            if onset <= offset:

                activity[
                    onset:offset + 1,
                    roi_index
                ] = 1

    return pd.DataFrame(
        activity,
        columns=rois
    )

def calculate_population_activity(
        activity_matrix: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate population-level activity from a binary activity matrix.

    For every frame, the numbre and fraction of active cells are
    calculated.

    Parameters
    ----------
    activity_matrix : pandas.DataFrame
        Binary cell-activity matrix produced by build_activity_matrix()

    Returns
    -------
    pandas.DataFrame
        DataFrame containing population activity for every frame.

        Columns
        -------
        n_active_cells : int
            Number of simultaneously active cells.
        
        fraction_active : float
            Fraction of all cells that are active
    """

    if activity_matrix.empty:
        return pd.DataFrame(
            columns = [
                "n_active_cells",
                "fraction_active"
            ]
        )

    n_cells = activity_matrix.shape[1]

    n_active_cells = activity_matrix.sum(
        axis = 1
    )

    if n_cells > 0:

        fraction_active = (
            n_active_cells / n_cells
        )

    else:

        fraction_active = pd.Series(
            np.nan,
            index = activity_matrix.index
        )

    return pd.DataFrame(
        {
            "n_active_cells" : n_active_cells,
            "fraction_active" : fraction_active
        }
    )

def calculate_pairwise_coactivity(
        activity_matrix: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate pairwaise temporal coactivity between cells.

    Two cells are considered coactive during a frame when both cells
    are simultaneously active

    Parameters
    ----------
    activity_matrix : pandas.DataFrame
        Binary cell-activity matrix produced by build_activity_matrix()

    Returns
    -------
    pandas.DataFrame
        Symmetric pairwaise coactivity matrix.

        Each element [ROI_A, ROI_B] represents the fraction of
        recording frames in which ROI_A and ROI_B were simultaneously  active.
    """

    if activity_matrix.empty:
        return pd.DataFrame()

    activity = activity_matrix.to_numpy(
        dtype = float
    )

    n_frames = activity.shape[0]

    if n_frames == 0:
        return pd.DataFrame()

    overlap = activity.T @ activity

    coactivity = overlap / n_frames

    return pd.DataFrame(
        coactivity,
        index = activity_matrix.columns,
        columns = activity_matrix.columns
    )

def calculate_event_overlap(
        profiles: dict[str, list[EventAnalysis]]
) -> pd.DataFrame:
    """
    Calculate event-based temporal overlap between pairs of cells.

    Two events are considered overlapping when their temporal intervals intersect.

    Parameters
    ----------
    profiles : dict[str, list[EventAnalysis]]
        Dictionary containing the EventAnalysis objects for each ROI.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing one row for every pair of ROIs.

        Columns
        -------
        ROI_A : str
            first ROI
        ROI_B : str
            second ROI
        overlapping_events : int
            Number of event pairs that overlap in time
    """

    rois = list(profiles.keys())

    results = []

    for i in range(len(rois)):

        roi_a = rois[i]

        for j in range(i + 1, len(rois)):

            roi_b = rois[j]

            events_a = profiles[roi_a]
            events_b = profiles[roi_b]

            overlapping_events = 0

            for event_a in events_a:
                onset_a = event_a.event.onset
                offset_a = event_a.event.offset

                for event_b in events_b:

                    onset_b = event_b.event.onset
                    offset_b = event_b.event.offset

                    if (
                        onset_a <= offset_b
                        and onset_b <= offset_a
                    ):

                        overlapping_events +=1

    results.append(
        {
            "RPO_A": roi_a,
            "ROI_B": roi_b,
            "overlapping_events": overlapping_events
        }
    )

    return pd.DataFrame(results)

