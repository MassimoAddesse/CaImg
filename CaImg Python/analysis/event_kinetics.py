import numpy as np

def rise_time(
        event_trace,
        fraction
):
    """
    Compute event rise time.

    Parameters
    ----------
    event_trace : np.ndarray
        Event fluorescence trace.

    fraction : float 
        Fraction of the peak amplitude
        used as threshold.

    Returns
    -------
    float
        Number of frames required to
        reach the selected fraction of the event peak.
    """
    if len(event_trace) == 0:
        return np.nan
    
    if not 0 < fraction <= 1:
        raise ValueError(
            "fraction must be between 0 and 1"
        )

    peak = np.max(event_trace)

    threshold = peak * fraction

    idx = np.where(
        event_trace >= threshold
    )[0]

    if len(idx) == 0:
        return np.nan

    return idx[0]

def decay_time(
        event_trace,
        fraction
):
    """
    Compute event decay time.

    Parameters
    ----------
    event_trace : np.ndarray
        Event fluorescence trace.

    fraction : float
        Fraction of the peak amplitude
        used as threshold.

    Returns
    -------
    float
        Number of frames between the 
        last threshold crossing and the end of the event.
    """
    
    if len(event_trace) == 0:
        return np.nan
    
    if not 0 < fraction <= 1:
        raise ValueError(
            "fraction must be between 0 and 1"
        )
    
    peak = np.max(event_trace)

    threshold = peak * fraction

    idx = np.where(
        event_trace >= threshold
    )[0]

    if len(idx) == 0:
        return np.nan

    return(
        len(event_trace)-1
        -
        idx[-1]
    )

def rise_speed(
        peak,
        rise_t
):
    """
    Compute rise speed.

    Parameters
    ----------
    peak : float
        Event peak amplitude.

    rise_t : float
        Event rise time.

    Returns
    -------
    float
        Peak amplitude divided by
        rise time.
    """    
    if rise_t <= 0:
        return np.nan
        
    return peak / rise_t
    
def decay_speed(
        peak,
        decay_t
):
    """
    Compute decay speed.

    Parameters
    ----------
    peak : float
        Event peak amplitude.

    decay_t : float
        Event decay time.

    Returns
    -------
    float
        Peak amplitude divided by
        decay time.
    """
    if decay_t <= 0:
        return np.nan
    
    return peak / decay_t

def event_peak(
        event_trace
):
    """
    Compute the peak amplitude
    of an event.

    Parameters
    ----------
    event_trace : np.ndarray
        Event fluoresnce trace.

    Returns
    -------
    float
        Maximum dF/F0 value.
    """
    if len(event_trace) == 0:
        return np.nan
    
    return np.max(event_trace)

def event_integral(
        event_trace,
        dt = 1
):
    """
    Compute the event area under the curve (AUC).

    Parameters
    ----------
    event_trace : np.ndarray
        Event fluoresnce trace.

    dt : float, optional
        Sampling interval.

    Returns
    -------
    float
        Event AUC estimated using the
        trapezoidal rule.
    """

    return np.trapezoid(
        event_trace,
        dx = dt
    )

def event_std(
        event_trace
):
    """
    Compute the standard deviation
    of an event trace.

    Parameters
    ----------
    event_trace : np.ndarray
    
    Returns
    -------
    float
        Event standard deviation.
    """

    return np.std(event_trace)