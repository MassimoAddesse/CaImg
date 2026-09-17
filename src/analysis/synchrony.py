import numpy as np
import pandas as pd

from metrics.event_analysis import EventAnalysis

def calculate_event_synchrony(
        profiles: dict[str, list[EventAnalysis]],
        tolerance_frames: int = 2
) -> pd.DataFrame:
    """
    Calculate pairwise event-based synchrony between cells.

    Two calcium events are considered synchronous when their onset
    times occur within the specified temporal tolerance.

    Parameters
    ----------
    profiles : dict[str, list[EventAnalysis]]
        Dictionary containing the EventAnalysis objects for each ROI.
        The ROI identifier is used as the dictionary key.

    tolerance_frames : int, optional
        Maximum allowed difference between the onset frames of two
        events for them to be considered synchronous.

        A value of 0 requres the events to start on the same frame.

    Returns
    -------
    pandas.DataFrame
        Symmetric pairwise synchrony matrix.

        Each value represents the fraction of events from the first ROI
        that have a synchronous event in the second ROI.
    """

    if tolerance_frames < 0:
        raise ValueError(
            "tolerance_frames myst be non-negative"
        )

    rois = list(profiles.keys())

    synchrony = np.zeros(
        (len(rois), len(rois)),
        dtype = float
    )

    for i in range(len(rois)):

        roi_a = rois[i]

        events_a = profiles[roi_a]

        if len(events_a) > 0:
            synchrony[i, i] = 1.0

        for j in range(i + 1, len(rois)):

            roi_b = rois[j]

            events_b = profiles[roi_b]

            if len(events_a) == 0 or len(events_b) == 0:
                synchrony[i, j] = np.nan
                synchrony[j, i] = np.nan

                continue

            onsets_a = np.array(
                [
                    profiler.event.onset
                    for profiler in events_a
                ],
                dtype = float
            )

            onsets_b = np.array(
                [
                    profiler.event.onset
                    for profiler in events_b
                ],
                dtype = float
            )

            synchronous_events = 0

            for onset_a in onsets_a:

                differences = np.abs(
                    onsets_b - onset_a
                )

                if np.any(
                    differences <= tolerance_frames
                ):
                    synchronous_events += 1

            synchrony_a_to_b = (
                synchronous_events / len(onsets_a)
            )

            synchronous_events = 0

            for onset_b in onsets_b:

                differences = np.abs(
                    onsets_a - onset_b
                )

                if np.any(
                    differences <= tolerance_frames
                ):
                    synchronous_events +=1

            synchrony_b_to_a = (
                synchronous_events / len(onsets_b)
            )

            synchrony_value = (
                synchrony_a_to_b +
                synchrony_b_to_a
            ) / 2.0

            synchrony[i, j] = synchrony_value
            synchrony[j, i] = synchrony_value


    return pd.DataFrame(
        synchrony,
        index = rois,
        columns = rois
    )

