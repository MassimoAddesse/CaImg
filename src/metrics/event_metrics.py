import numpy as np

from detection.base import DetectionEvent


def calculate_amplitude(
    event: DetectionEvent,
    dff: np.ndarray
) -> float:
    """
    Calculate the amplitude of a single calcium event.

    The amplitude is defined as the difference between
    the DFF value at the peak and the DFF value at onset.

    Parameters
    ----------
    event : DetectionEvent
        Detected calcium event containing the onset and
        peak frame indices.

    dff : np.ndarray
        Original DFF trace of the ROI.

    Returns
    -------
    float
        Amplitude of the calcium event expressed as ΔF/F.
    """

    baseline = dff[event.onset]
    peak = dff[event.peak]

    return peak - baseline


def calculate_auc(
    event: DetectionEvent,
    dff: np.ndarray,
    sampling_rate: float
) -> float:
    """
    Calculate the area under the curve (AUC) of a
    single calcium event.

    The baseline is defined as the DFF value at onset.
    The area is calculated between onset and offset.

    Parameters
    ----------
    event : DetectionEvent
        Detected calcium event containing the onset and
        offset frame indices.

    dff : np.ndarray
        Original DFF trace of the ROI.

    sampling_rate : float
        Sampling rate of the recording in Hz.

    Returns
    -------
    float
        Area under the event curve expressed as
        DFF * seconds.
    """

    baseline = dff[event.onset]

    event_trace = (
        dff[event.onset:event.offset + 1]
        - baseline
    )

    dt = 1.0 / sampling_rate

    return np.trapezoid(
        event_trace,
        dx=dt
    )


def calculate_duration(
    event: DetectionEvent,
    sampling_rate: float
) -> float:
    """
    Calculate the total duration of a single calcium event.

    Duration is measured from onset to offset.

    Parameters
    ----------
    event : DetectionEvent
        Detected calcium event containing onset and
        offset frame indices.

    sampling_rate : float
        Sampling rate of the recording in Hz.

    Returns
    -------
    float
        Event duration in seconds.
    """

    return (
        event.offset - event.onset
    ) / sampling_rate


def calculate_rise_time(
    event: DetectionEvent,
    sampling_rate: float
) -> float:
    """
    Calculate the rise time of a calcium event.

    Rise time is measured from onset to peak.

    Parameters
    ----------
    event : DetectionEvent
        Detected calcium event containing onset and
        peak frame indices.

    sampling_rate : float
        Sampling rate of the recording in Hz.

    Returns
    -------
    float
        Rise time in seconds.
    """

    return (
        event.peak - event.onset
    ) / sampling_rate


def calculate_decay_time(
    event: DetectionEvent,
    sampling_rate: float
) -> float:
    """
    Calculate the decay time of a calcium event.

    Decay time is measured from peak to offset.

    Parameters
    ----------
    event : DetectionEvent
        Detected calcium event containing peak and
        offset frame indices.

    sampling_rate : float
        Sampling rate of the recording in Hz.

    Returns
    -------
    float
        Decay time in seconds.
    """

    return (
        event.offset - event.peak
    ) / sampling_rate


def calculate_rise_speed(
    event: DetectionEvent,
    dff: np.ndarray,
    sampling_rate: float
) -> float:
    """
    Calculate the average rise speed of a calcium event.

    Rise speed is calculated as event amplitude divided
    by rise time.

    Parameters
    ----------
    event : DetectionEvent
        Detected calcium event.

    dff : np.ndarray
        Original DFF trace of the ROI.

    sampling_rate : float
        Sampling rate of the recording in Hz.

    Returns
    -------
    float
        Average rise speed expressed as DFF per second.
    """

    rise_time = calculate_rise_time(
        event,
        sampling_rate
    )

    if rise_time <= 0:
        return np.nan

    amplitude = calculate_amplitude(
        event,
        dff
    )

    return amplitude / rise_time


def calculate_decay_speed(
    event: DetectionEvent,
    dff: np.ndarray,
    sampling_rate: float
) -> float:
    """
    Calculate the average decay speed of a calcium event.

    The returned value is the positive magnitude of the
    average decay rate.

    Parameters
    ----------
    event : DetectionEvent
        Detected calcium event.

    dff : np.ndarray
        Original DFF trace of the ROI.

    sampling_rate : float
        Sampling rate of the recording in Hz.

    Returns
    -------
    float
        Average decay speed expressed as DFF per second.
    """

    decay_time = calculate_decay_time(
        event,
        sampling_rate
    )

    if decay_time <= 0:
        return np.nan

    peak = dff[event.peak]
    offset = dff[event.offset]

    return (
        peak - offset
    ) / decay_time


def calculate_rise_time_10_90(
    event: DetectionEvent,
    dff: np.ndarray,
    sampling_rate: float
) -> float:
    """
    Calculate the 10-90% rise time of a calcium event.

    The measurement starts when the signal reaches 10%
    of the event amplitude and ends when it reaches 90%
    of the event amplitude.

    Linear interpolation is used between frames.

    Parameters
    ----------
    event : DetectionEvent
        Detected calcium event.

    dff : np.ndarray
        Original DFF trace of the ROI.

    sampling_rate : float
        Sampling rate of the recording in Hz.

    Returns
    -------
    float
        10-90% rise time in seconds.
    """

    baseline = dff[event.onset]
    peak = dff[event.peak]

    amplitude = peak - baseline

    if amplitude <= 0:
        return np.nan

    level_10 = baseline + 0.10 * amplitude
    level_90 = baseline + 0.90 * amplitude

    rise_trace = dff[
        event.onset:event.peak + 1
    ]

    t10 = _find_rising_crossing(
        rise_trace,
        level_10
    )

    t90 = _find_rising_crossing(
        rise_trace,
        level_90
    )

    if t10 is None or t90 is None:
        return np.nan

    return (
        t90 - t10
    ) / sampling_rate


def calculate_decay_time_10_90(
    event: DetectionEvent,
    dff: np.ndarray,
    sampling_rate: float
) -> float:
    """
    Calculate the 90–10% decay time of a calcium event.

    The measurement starts when the signal falls through
    90% of the event amplitude and ends when it reaches
    10% of the event amplitude.

    Linear interpolation is used between frames.

    Parameters
    ----------
    event : DetectionEvent
        Detected calcium event.

    dff : np.ndarray
        Original DFF trace of the ROI.

    sampling_rate : float
        Sampling rate of the recording in Hz.

    Returns
    -------
    float
        90–10% decay time in seconds.
    """

    baseline = dff[event.onset]
    peak = dff[event.peak]

    amplitude = peak - baseline

    if amplitude <= 0:
        return np.nan

    level_10 = baseline + 0.10 * amplitude
    level_90 = baseline + 0.90 * amplitude

    decay_trace = dff[
        event.peak:event.offset + 1
    ]

    t90 = _find_decay_crossing(
        decay_trace,
        level_90
    )

    t10 = _find_decay_crossing(
        decay_trace,
        level_10
    )

    if t90 is None or t10 is None:
        return np.nan

    return (
        t10 - t90
    ) / sampling_rate


def calculate_rise_speed_10_90(
    event: DetectionEvent,
    dff: np.ndarray,
    sampling_rate: float
) -> float:
    """
    Calculate the average rise speed between 10% and 90%
    of the event amplitude.

    Parameters
    ----------
    event : DetectionEvent
        Detected calcium event.

    dff : np.ndarray
        Original DFF trace of the ROI.

    sampling_rate : float
        Sampling rate of the recording in Hz.

    Returns
    -------
    float
        Average 10–90% rise speed expressed as DFF
        per second.
    """

    rise_time = calculate_rise_time_10_90(
        event,
        dff,
        sampling_rate
    )

    if rise_time <= 0 or np.isnan(rise_time):
        return np.nan

    amplitude = calculate_amplitude(
        event,
        dff
    )

    return (
        0.80 * amplitude
    ) / rise_time


def calculate_decay_speed_10_90(
    event: DetectionEvent,
    dff: np.ndarray,
    sampling_rate: float
) -> float:
    """
    Calculate the average decay speed between 90% and 10%
    of the event amplitude.

    The returned value is the positive magnitude.

    Parameters
    ----------
    event : DetectionEvent
        Detected calcium event.

    dff : np.ndarray
        Original DFF trace of the ROI.

    sampling_rate : float
        Sampling rate of the recording in Hz.

    Returns
    -------
    float
        Average 90–10% decay speed expressed as DFF
        per second.
    """

    decay_time = calculate_decay_time_10_90(
        event,
        dff,
        sampling_rate
    )

    if decay_time <= 0 or np.isnan(decay_time):
        return np.nan

    amplitude = calculate_amplitude(
        event,
        dff
    )

    return (
        0.80 * amplitude
    ) / decay_time


def calculate_fwhm(
    event: DetectionEvent,
    dff: np.ndarray,
    sampling_rate: float
) -> float:
    """
    Calculate the full width at half maximum (FWHM)
    of a calcium event.

    The width is measured at 50% of the event amplitude.

    Parameters
    ----------
    event : DetectionEvent
        Detected calcium event.

    dff : np.ndarray
        Original DFF trace of the ROI.

    sampling_rate : float
        Sampling rate of the recording in Hz.

    Returns
    -------
    float
        FWHM of the event in seconds.
    """

    baseline = dff[event.onset]
    peak = dff[event.peak]

    amplitude = peak - baseline

    if amplitude <= 0:
        return np.nan

    half_max = baseline + 0.50 * amplitude

    event_trace = dff[
        event.onset:event.offset + 1
    ]

    indices = np.where(
        event_trace >= half_max
    )[0]

    if len(indices) < 2:
        return np.nan

    first = indices[0]
    last = indices[-1]

    return (
        last - first
    ) / sampling_rate


def _find_rising_crossing(
    trace: np.ndarray,
    level: float
) -> float | None:
    """
    Find the interpolated crossing point of a rising signal.

    Parameters
    ----------
    trace : np.ndarray
        Rising portion of the DFF trace.

    level : float
        DFF level at which the crossing is searched.

    Returns
    -------
    float or None
        Interpolated frame position of the crossing.
        Returns None if the level is not reached.
    """

    for i in range(1, len(trace)):

        if trace[i] >= level:

            y1 = trace[i - 1]
            y2 = trace[i]

            if y2 == y1:
                return float(i)

            fraction = (
                (level - y1)
                / (y2 - y1)
            )

            return i - 1 + fraction

    return None


def _find_decay_crossing(
    trace: np.ndarray,
    level: float
) -> float | None:
    """
    Find the interpolated crossing point of a decaying signal.

    Parameters
    ----------
    trace : np.ndarray
        Decaying portion of the DFF trace.

    level : float
        DFF level at which the crossing is searched.

    Returns
    -------
    float or None
        Interpolated frame position of the crossing.
        Returns None if the level is not reached.
    """

    for i in range(1, len(trace)):

        if trace[i] <= level:

            y1 = trace[i - 1]
            y2 = trace[i]

            if y2 == y1:
                return float(i)

            fraction = (
                (y1 - level)
                / (y1 - y2)
            )

            return i - 1 + fraction

    return None