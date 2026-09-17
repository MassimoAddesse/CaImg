import pandas as pd

from .base import DetectionResult


def detect_all_cells(
    dff_df: pd.DataFrame,
    detector
) -> dict[str, DetectionResult]:
    """
    Detect calcium events independently for every ROI.

    Each column of the DFF dataframe is treated as the
    DFF trace of one ROI/cell.

    Parameters
    ----------
    dff_df : pandas.DataFrame
        DFF dataframe where each column represents one ROI.

    detector : EventDetector
        Event detector used to identify calcium events.

    Returns
    -------
    dict[str, DetectionResult]
        Dictionary containing one DetectionResult for each
        ROI. The ROI identifier is used as the dictionary key.
    """

    results = {}

    for roi in dff_df.columns:

        dff = dff_df[roi].to_numpy(
            dtype=float
        )

        result = detector.detect(
            dff = dff,
            roi = roi
        )

        result.events.sort(
            key=lambda event: event.onset
        )

        for event_id, event in enumerate(
            result.events,
            start=1
        ):
            event.event_id = event_id

        results[roi] = result

    return results
