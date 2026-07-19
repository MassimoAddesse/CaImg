from dataio.excel_loader import load_fluorescence
from dataio.controls_loader import load_controls

from analysis.compute_threshold import compute_threshold

from pipeline import CalciumAnalysis
from models import AnalysisConfig

import time
import numpy as np


INPUT_FILE = r"D:\ROIs\Fox\Foxg1 1.csv"

CONTROLS_DIR = r"D:\ROIs\Controls"


def run_analysis():

    config = AnalysisConfig()

    controls = load_controls(
        CONTROLS_DIR
    )

    threshold = compute_threshold(
        controls,
        factor=config.threshold_factor,
        half_window=config.half_window,
        edge_margin=config.edge_margin
    )

    config.threshold = threshold

    recording = load_fluorescence(
        INPUT_FILE
    )

    analysis = CalciumAnalysis(
        config
    )

    results = analysis.run(
        recording
    )

    return results, threshold


def main():

    n_runs = 30

    times = []

    print("\nBenchmark started\n")

    for i in range(n_runs + 1):

        start = time.perf_counter()

        results, threshold = run_analysis()

        elapsed = (
            time.perf_counter()
            - start
        )

        if i == 0:

            print(
                f"Warmup: {elapsed:.3f} s"
            )

        else:

            times.append(
                elapsed
            )

            print(
                f"Run {i:02d}: "
                f"{elapsed:.3f} s"
            )

    profiler1 = results["profiler1"]

    profiler2 = results["profiler2"]

    print("\nProfiler1")

    print(
        profiler1["all_cells_dff_df"].shape
    )

    print(
        profiler1["active_cells_dff_df"].shape
    )

    print(
        profiler1["summary"]
        .head()
    )

    print("\nProfiler2")

    print(
        len(profiler2)
    )

    print("\nBenchmark")

    print(
        f"Threshold: "
        f"{threshold:.6f}"
    )

    print(
        f"Mean : "
        f"{np.mean(times):.3f} s"
    )

    print(
        f"Std  : "
        f"{np.std(times):.3f} s"
    )

    print(
        f"Min  : "
        f"{np.min(times):.3f} s"
    )

    print(
        f"Max  : "
        f"{np.max(times):.3f} s"
    )


if __name__ == "__main__":
    main()