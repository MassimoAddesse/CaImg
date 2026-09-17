import numpy as np
import pandas as pd

def local_min_f0(
        signal: np.ndarray,
        half_window: int,
        edge_margin: int
) -> np.ndarray:
    """
    Compute the local fluorescence baseline (F0)
    using a rolling minimum window.

    The baseline at frame t is the minimum fluorescence within:
        [t - half_window, ..., t, ..., t + half_window]

    Parameters
        ----------
        signal : np.ndarray
            Fluorescence trace of a single neuron.

        half_window : int, optional
            Half-width of the normalization window. 
            A value of 20 corresponds to a window
            of 41 frames (20 before and 20 after the current frame).

        edge_margin : int, optional
            Number of frames to ignore at the edges of the recordings.
            This is to avoid edge effects.

        Returns
        -------
        np.ndarray
            Local baseline (F0) for each frame.

    Frames within edge_margin of the start and end of the recording
    will be set to np.nan.
    
    """

    if half_window < 0:
        raise ValueError(
            "half_window must be non-negative"
        )

    if edge_margin < 0:
        raise ValueError(
            "edge_margin must be non-negative"
        )      

    signal = np.asarray(
        signal,
        dtype = float
    )

    if signal.size == 0: 
        raise ValueError(
            "signal cannot be empty"
        )

    n = len(signal)

    f0 = np.full(
        n,
        np.nan,
        dtype = float
    )

    start_frame = edge_margin
    stop_frame = n - edge_margin

    for t in range(
        start_frame, 
        stop_frame
    ):

        start = t - half_window
        stop = t + half_window + 1
        f0[t] = np.min(signal[start:stop])

    return f0

    
def compute_dff(
        signal: np.ndarray,
        f0: np.ndarray,
        epsilon: float
) -> np.ndarray:

    """
    Compute the normalized fluorescence change
    (dF/F0).

    Parameters
    ----------
    signal : np.ndarray
        Raw fluorescence trace of a single neuron.

    f0 : np.ndarray
        Local baseline (F0) for each frame.

    Returns
    -------
    np.ndarray
        Normalized fluorescence change (dF/F0) for each frame.

    Notes
    -----
    Df/F0 is computed as:

        (F - F0) / (F0 + eps)
            a small epsilon is added to avoid division by zero.
    """

    signal = np.asarray(
        signal,
        dtype = float
    )

    f0 = np.asarray(
        f0,
        dtype = float
    )

    if signal.shape != f0.shape:
        raise ValueError(
            "signal and f0 must have the same change"
        )

    return (
        (signal - f0)
        / (f0 + epsilon)
    )

def calculate_dff_dataframe(
        fluorescence: pd.DataFrame,
        config
) -> tuple[pd.DataFrame, pd.DataFrame]:

    dff = pd.DataFrame(
        index = fluorescence.index,
        columns = fluorescence.columns,
        dtype = float
    )

    f0_df = pd.DataFrame(
        index = fluorescence.index,
        columns= fluorescence.columns,
        dtype = float
    )

    for cell_name in fluorescence.columns: 

        signal = fluorescence[cell_name].to_numpy()

        f0 = local_min_f0(
            signal,
            half_window = config.half_window,
            edge_margin = config.edge_margin
        )

        cell_dff = compute_dff(
            signal,
            f0,
            epsilon = config.eps
        )

        f0_df[cell_name] = f0
        dff[cell_name] = cell_dff

    return dff, f0_df
