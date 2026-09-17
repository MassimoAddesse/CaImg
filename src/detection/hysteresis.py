import numpy as np

def find_hysteresis_boundaries(
        signal: np.ndarray,
        peak_indices: np.ndarray,
        threshold_low: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:

    """
    Determine event onset and offset using hysteresis.

    A peak is considered part of an event only after it has
    crossed the high threshold. Once the peak is identified,
    the event boundaries are extended until the signal falls
    below the lower threshold.

    Parameters
    ----------
    signal : np.ndarray
        Original DFF trace
    
    peak_indices : np.ndarray
        Indices of detected peaks.

    threshold_low : np.ndarray
        Lower threshold for each frame.

    Returns
    -------
    onset_indices : np.ndarray
        Event onset for each detected peak.

    offset_indices : np.ndarray
        Event offset for each detected peak.
    """

    signal = np.asarray(signal, dtype = float)
    peak_indices = np.asarray(peak_indices, dtype = int)
    threshold_low = np.asarray(threshold_low, dtype = float)

    if signal.ndim != 1:
        raise ValueError("Signal must be one-dimensional.")
    if threshold_low.shape != signal.shape:
        raise ValueError(
            "threshold_low must have the same shape as signal"
        )

    onsets = []
    offsets = []

    for peak in peak_indices:

        onset = peak

        while onset > 0:
            previous = onset - 1

            if (
                np.isnan(signal[previous])
                or np.isnan(threshold_low[previous])
            ):
                break
            if signal[previous] < threshold_low[previous]:
                break

            onset = previous

        offset = peak

        while offset < len(signal) - 1:
            following = offset + 1
            if (
                np.isnan(signal[following])
                or np.isnan(threshold_low[following])
            ):
                break
            if signal[following] < threshold_low[following]:
                break

            offset = following

        onsets.append(onset)
        offsets.append(offset)

    return (
        np.asarray(onsets, dtype = int),
        np.asarray(offsets, dtype = int)
    )
