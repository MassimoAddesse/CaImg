import numpy as np

def local_min_f0(
        signal,
        half_window = 20
    ):
        
        """"
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

        Returns
        -------
        np.ndarray
            Local baseline (F0) for each frame.
    
        """
        
        n = len(signal)

        f0 = np.zeros(n)

        for t in range(n):
        
            start = max(0, t - half_window)

            stop = min(n, t + half_window + 1)

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
    eps = 1e-12
    
    res = ((signal - f0) / (f0 + eps))
    
    return res

