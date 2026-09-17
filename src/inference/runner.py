from __future__ import annotations

import numpy as np
import pandas as pd

from .base import InferenceResult, SpikeInference


def run_inference(
    dff_df: pd.DataFrame,
    detector: SpikeInference,
) -> dict[str, InferenceResult]:
    results: dict[str, InferenceResult] = {}

    for roi in dff_df.columns:
        results[str(roi)] = detector.infer(
            dff=dff_df[roi].to_numpy(dtype=float),
            roi=str(roi),
        )

    return results


def inference_to_dataframe(
    results: dict[str, InferenceResult],
) -> pd.DataFrame:
    if not results:
        return pd.DataFrame()

    max_len = max(len(r.spike_activity) for r in results.values())
    data = {}

    for roi, result in results.items():
        values = np.asarray(result.spike_activity, dtype=float)
        if len(values) < max_len:
            padded = np.full(max_len, np.nan)
            padded[:len(values)] = values
            values = padded
        data[roi] = values

    return pd.DataFrame(data)


def inference_events_to_dataframe(
    results: dict[str, InferenceResult],
) -> pd.DataFrame:
    rows = []

    for roi, result in results.items():
        events = result.spike_events
        if events is None:
            continue

        activity = np.asarray(result.spike_activity, dtype=float)

        for event_id, frame in enumerate(events, start=1):
            frame = int(frame)
            rows.append({
                "ROI": roi,
                "Event": event_id,
                "Frame": frame,
                "Time_s": frame / result.sampling_rate,
                "Inferred_activity": (
                    float(activity[frame])
                    if np.isfinite(activity[frame])
                    else np.nan
                ),
            })

    return pd.DataFrame(rows)