import numpy as np

def local_min_f0(
        signal,
        half_window = 20,
        edge_margin = 50
    ):
        
        """
        Compute local fluorescence baseline (F0) 
        using a rolling minimum window.

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
        
        if len(signal) == 0:
            raise ValueError(
                "signal cannot be empty"
            )
        
        signal = np.asarray(signal)

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
        signal, 
        f0
    ):
    
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
    
    eps = 1e-12
    
    res = ((signal - f0) / (f0 + eps))
    
    return res

