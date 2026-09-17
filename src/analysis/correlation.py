import numpy as np
import pandas as pd

def calculate_pearson_correlation(
        dff_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate pairwise Pearson correlation between ROI DFF traces.

    Pearson correlation measures the linear similarity between the
    temporal fluorescence profiles of pairs of cells.

    Parameters
    ----------
    dff_df : pandas.DataFrame
        DFF dataframe where each column represents one ROI and
        each row represents one frame.

    Returns
    -------
    pandas.DataFrame
        Symmetric pairwise Pearson correlation matrix.

        Values range from -1 to 1:

        1  -> highly similar temporal activity
        0  -> no linear correlation
        -1 -> opposite temporal activity
    """

    if dff_df.empty:
        return pd.DataFrame()

    return dff_df.corr(
        method="pearson"
    )

def calculate_spearman_correlation(
        dff_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate pairwise Spearman correlation between ROI DFF traces.

    Spearman correlation measures the similarity between the temporal
    ranking of fluorescence values and is less sensitive to outliers
    than Pearson correlation.

    Parameters
    ----------
    dff_df : pandas.DataFrame
            DFF dataframe where each column represents one ROI and
            each row represents one frame.
    
    Returns
    -------
    pandas.DataFrame
        Symmetric pairwise Spearman correlation matrix.
    
        Values range from -1 to 1
    """

    if dff_df.empty:
        return pd.DataFrame()

    return dff_df.corr(
        method="spearman"
    )

def calculate_lagged_correlation(
        dff_df: pd.DataFrame,
        max_lag_frames: int = 3
) -> dict[tuple[str, str], pd.DataFrame]:
    """
    Calculate Pearson correlation between pairs of the ROIs at different
    temporal lags.
    This can identify whether the activity of one cell tends to precede
    or follow the activitiy of another cell

    Parameters
    ----------
    dff_df : pandas.DataFrame
        DFF dataframe where each column represents one ROI.

    max_lag_frames : int
        Maximum positive and negative temporal lag to evaluate

    Returns
    -------
    dict[tuple[str, str], pandas.DataFrame]
        Dictionary containing one dataframe for every pair of ROIs.

        Each dataframe contains:
        
        lag : temporal lag in frames
        correlation : Pearson correlation at that lag
    """

    if max_lag_frames < 0:
        raise ValueError(
            "max_lag_frames must be non-negative"
        )

    rois = list(dff_df.columns)

    results = {}

    for i in range(len(rois)):

        roi_a = rois[i]

        trace_a = dff_df[roi_a].to_numpy(
            dtype = float
        )

        for j in range(i + 1, len(rois)):

            roi_b = rois[j]

            trace_b = dff_df[roi_b].to_numpy(
                dtype = float
            )

            lags = []
            correlations = []

            for lag in range(
                -max_lag_frames,
                max_lag_frames + 1
            ):

                if lag < 0:
                    
                    x = trace_a[:lag]
                    y = trace_b[-lag:]

                elif lag > 0:

                    x = trace_a[lag:]
                    y = trace_b[:-lag]

                else:

                    x = trace_a
                    y = trace_b

                if len(x) < 2:
                    
                    correlation = np.nan

                elif (
                    np.std(x) == 0
                    or np.std(y) == 0
                ):

                    correlation = np.nan

                else:

                    correlation = np.corrcoef(
                        x,
                        y
                    )[0, 1]

                lags.append(lag)
                correlations.append(correlation)

            results[(roi_a, roi_b)] = pd.DataFrame(
                {
                    "lag": lags,
                    "correlation": correlations
                }
            )

    return results