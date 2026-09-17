from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from .base import InferenceResult

def plot_trace_with_inferred_spikes(
        dff: ndarray,
        result: InferenceResult,
        output_path: str | Path | None = None,
        title: str | None = None,
        start_frame: int = 0,
        end_frame: int | None = None
) -> plt.Figure:
    dff = np.asarray(dff, dtype = float)
    activity = np.asarray(result.spike_activity, dtype = float)

    if end_frame is None:
        end_frame = len(dff)

    start_frame = max(0, int(start_frame))
    end_frame = min(len(dff), int(end_frame))

    frames = np.arange(start_frame, end_frame)
    time = frames / result.sampling_rate

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 5.5), sharex = True,
        gridspec_kw = {"height_ratios": [3, 1]}
    )

    ax1.plot(time, dff[start_frame:end_frame], linewidth = 1.5)
    ax1.set_ylabel(r"$\Delta F/F$")
    ax1.set_title(
        title or f"{result.roi} - calcium trace and inferred activity"
    )
    ax1.grid(alpha = 0.2)

    inferred = activity[start_frame:end_frame]
    ax2.plot(time_inferred, linewidth = 1.2)
    ax2.fill_between(time, 0, inferred, alpha = 0.18)
    
    events = np.asarray(
        result.spike_events if result.spike_events is not None else [],
        dtype = int
    )
    events = events[(events >= start_frame) & (events < end_frame)]

    for frame in events:
        value = activity[frame]
        if np.isfinite(value):
            ax2.vlines(
                frame / result.sampling_rate,
                0,
                value,
                linewidth = 1.2
            )

    ax2.set_ylabel("Inferred\nactivity")
    ax2.set_xlabel("Time (s)")
    ax2.grid(alpha = 0.2)

    fig.tight_layout()

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents = True, exist_ok = True)
        fig.savefig(output_path, dpi = 300, bbox_inches = "tight")

    return fig