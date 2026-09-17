"""Event-level OASIS spike inference for CaImg Analyzer.

Uses the calcium events already detected by CaImg Analyzer and counts how
many individual OASIS-inferred spikes fall inside each event's onset-offset.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

try:
    from oasis.functions import deconvolve
except ImportError as exc:
    raise ImportError("Install OASIS with: pip install oasis-deconv") from exc


@dataclass
class EventSpikeInferenceConfig:
    sampling_rate: float = 4.0
    tau_d: float | None = None
    tau_r: float | None = None
    prominence_k: float = 2.5
    min_spike_distance_frames: int = 1
    fallback_prominence: float = 1e-4
    allow_nan: bool = True


def estimate_noise(activity: np.ndarray) -> float:
    """Robust noise estimate from first differences."""
    x = np.asarray(activity, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 3:
        return 0.0
    d = np.diff(x)
    mad = np.median(np.abs(d - np.median(d)))
    sigma = mad / (0.6745 * np.sqrt(2.0))
    return float(sigma) if np.isfinite(sigma) else 0.0


def run_oasis(dff: np.ndarray, config: EventSpikeInferenceConfig) -> np.ndarray:
    """Run OASIS while preserving NaN positions."""
    dff = np.asarray(dff, dtype=float)
    if dff.ndim != 1:
        raise ValueError("dff must be a 1D array")

    if not config.allow_nan and not np.all(np.isfinite(dff)):
        raise ValueError("DFF contains NaNs; use allow_nan=True")

    activity = np.full(dff.shape, np.nan, dtype=float)
    finite = np.flatnonzero(np.isfinite(dff))
    if len(finite) == 0:
        return activity

    breaks = np.where(np.diff(finite) > 1)[0]
    starts = np.r_[0, breaks + 1]
    ends = np.r_[breaks, len(finite) - 1]

    for a, b in zip(starts, ends):
        idx = finite[a:b + 1]
        if len(idx) < 3:
            continue
        kwargs = {"framerate": config.sampling_rate}
        if config.tau_d is not None:
            kwargs["tau_d"] = config.tau_d
        if config.tau_r is not None:
            kwargs["tau_r"] = config.tau_r
        result = deconvolve(dff[idx], **kwargs)
        activity[idx] = np.asarray(result.s, dtype=float)

    return activity


def detect_inferred_spikes(
    activity: np.ndarray,
    roi: str,
    config: EventSpikeInferenceConfig,
) -> tuple[pd.DataFrame, float, float]:
    """Detect individual peaks in OASIS activity using adaptive prominence."""
    valid = np.isfinite(activity)
    frames = np.flatnonzero(valid)
    x = np.asarray(activity[valid], dtype=float)
    if len(x) == 0:
        return pd.DataFrame(columns=["ROI", "Spike", "Frame", "Time_s", "OASIS_activity"]), 0.0, 0.0

    sigma = estimate_noise(x)
    prominence = config.prominence_k * sigma
    if not np.isfinite(prominence) or prominence <= 0:
        prominence = config.fallback_prominence

    peaks, props = find_peaks(
        x,
        prominence=prominence,
        distance=max(1, config.min_spike_distance_frames),
    )

    rows = []
    for spike_id, p in enumerate(peaks, start=1):
        frame = int(frames[p])
        rows.append({
            "ROI": roi,
            "Spike": spike_id,
            "Frame": frame,
            "Time_s": frame / config.sampling_rate,
            "OASIS_activity": float(x[p]),
        })

    return pd.DataFrame(rows), float(prominence), float(sigma)


def assign_spikes_to_events(
    events,
    spike_table: pd.DataFrame,
    roi: str,
    sampling_rate: float,
) -> pd.DataFrame:
    """Count inferred spikes inside each existing calcium transient."""
    rows = []
    spike_frames = (
        spike_table["Frame"].to_numpy(dtype=int)
        if not spike_table.empty else np.array([], dtype=int)
    )

    for event in events:
        onset = int(event.onset)
        peak = int(event.peak)
        offset = int(event.offset)
        mask = (spike_frames >= onset) & (spike_frames <= offset)
        matched = spike_frames[mask]

        rows.append({
            "ROI": roi,
            "Event": int(event.event_id),
            "Onset_frame": onset,
            "Peak_frame": peak,
            "Offset_frame": offset,
            "Onset_s": onset / sampling_rate,
            "Peak_s": peak / sampling_rate,
            "Offset_s": offset / sampling_rate,
            "Inferred_spike_count": int(len(matched)),
            "Inferred_spike_frames": ",".join(map(str, matched)),
            "Inferred_spike_times_s": ",".join(f"{f / sampling_rate:.3f}" for f in matched),
        })

    return pd.DataFrame(rows)


def infer_spikes_per_transient(
    dff: np.ndarray,
    roi: str,
    events,
    config: EventSpikeInferenceConfig | None = None,
):
    """Complete DFF -> OASIS -> spikes -> spikes-per-calcium-event analysis."""
    config = config or EventSpikeInferenceConfig()
    activity = run_oasis(dff, config)
    spikes, prominence, sigma = detect_inferred_spikes(activity, roi, config)
    event_table = assign_spikes_to_events(events, spikes, roi, config.sampling_rate)
    if not event_table.empty:
        event_table["OASIS_prominence"] = prominence
        event_table["OASIS_noise_sigma"] = sigma
    return activity, spikes, event_table


def analyze_all_rois(dff_df: pd.DataFrame, detection_results: dict,
                     config: EventSpikeInferenceConfig | None = None):
    """Run event-level inference for all ROIs in a DFF dataframe."""
    config = config or EventSpikeInferenceConfig()
    event_tables = []
    spike_tables = []

    for roi in dff_df.columns:
        if roi not in detection_results:
            continue
        result = detection_results[roi]
        activity, spikes, events = infer_spikes_per_transient(
            dff_df[roi].to_numpy(dtype=float), str(roi), result.events, config
        )
        if not events.empty:
            event_tables.append(events)
        if not spikes.empty:
            spike_tables.append(spikes)

    event_table = pd.concat(event_tables, ignore_index=True) if event_tables else pd.DataFrame()
    spike_table = pd.concat(spike_tables, ignore_index=True) if spike_tables else pd.DataFrame()
    return event_table, spike_table


def summarize_per_cell(event_table: pd.DataFrame) -> pd.DataFrame:
    """Cell-level summary of inferred spikes per calcium transient."""
    if event_table.empty:
        return pd.DataFrame()

    rows = []
    for roi, g in event_table.groupby("ROI"):
        n = g["Inferred_spike_count"].to_numpy(dtype=float)
        rows.append({
            "ROI": roi,
            "Calcium_events": len(n),
            "Total_inferred_spikes": int(n.sum()),
            "Mean_spikes_per_event": float(n.mean()),
            "Median_spikes_per_event": float(np.median(n)),
            "Fraction_events_2plus_spikes": float(np.mean(n >= 2)),
            "Fraction_events_3plus_spikes": float(np.mean(n >= 3)),
            "Max_spikes_in_event": int(n.max()),
        })
    return pd.DataFrame(rows)
