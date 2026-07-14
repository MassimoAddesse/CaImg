import numpy as np

def detect_on_states(
        dff,
        threshold
):
    
    """
    Covert a dF/F0 trace into a binary ON/OFF
    activity trace.

    Parameters
    ----------
    dff : np.ndarray
        df/F0 trace.

    threshold : float
        Event-detection threshold.

    Returns
    -------
    np.ndarray
        Boolean ON/OFF activity trace.
    """

    return dff >= threshold

def extract_events(
        binary_trace
):
    
    """
    Extract contiguous ON periods from a
    binary activity trace.

    Parameters
    ----------
    binary_trace : np.ndarray
        Boolean ON/OFF trace.

    Returns
    -------
    list[tuple]
        List of event intervals:

            (start_frame, end_frame)
    """

    events = []

    start = None

    for i, val in enumerate(binary_trace):

        if val and start is None:
            start = i

        if not val and start is not None:

            events.append(
                (start, i - 1)
            )

            start = None

    if start is not None:

        events.append(
            (
                start,
                len(binary_trace) - 1
            )
        )

    return events

def extract_iei(
        binary_trace
):
    
    """
    Extract inter-event intervals (IEIs) from a
    binary activity trace.

    Parameters
    ----------  
    binary_trace : np.ndarray
        Boolean ON/OFF trace.

    Returns
    -------
    list[tuple]
        List of inter-event intervals:

            (start_frame, end_frame)
    """

    off_trace = np.logical_not(
        binary_trace
    )

    return extract_events(
        off_trace
    )

