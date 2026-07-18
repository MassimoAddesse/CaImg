from dataio.excel_loader import load_fluorescence
from dataio.controls_loader import load_controls
from dataio.exporter import export_events
from analysis.compute_threshold import compute_threshold
from pipeline import CalciumAnalysis
from models import AnalysisConfig
from dataio.plotting import plot_dff_traces
import os

INPUT_FILE = r"d:\ROIs\Fox\Foxg1 1.csv"
CONTROLS_DIR = r"D:\ROIs\Controls"
OUTPUT_DIR = r"results"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

def main():

    try:

        config = AnalysisConfig()

        controls = load_controls(
            CONTROLS_DIR
        )

        threshold = compute_threshold(
            controls,
            factor=config.threshold_factor
        )

        print(
            f"Computed threshold: {threshold}")

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

        profiler1 = results[
            "profiler1"
        ]

        profiler2 = results[
            "profiler2"
        ]

        #profiler3 = results[
        #    "profiler3"
        #]

        profiler1["all_cells_dff_df"].to_excel(
            os.path.join(
                OUTPUT_DIR,
                "all_cells_dff.xlsx"
            )
        )

        profiler1["active_cells_dff_df"].to_excel(
            os.path.join(
                OUTPUT_DIR,
                "active_cells_dff.xlsx"
            )
        )

        profiler1["summary"].to_excel(
            os.path.join(
                OUTPUT_DIR,
                "profiler1_summary.xlsx"
            ),
            index = False
        )

        print(
            f"Analysis completed successfully: "
            f"{OUTPUT_DIR}"
        )

        export_events(
            results[
                "profiler2"
            ],
            os.path.join(
                OUTPUT_DIR,
                "profiler2_events.xlsx"
            )
        )

        plot_dff_traces(

            profiler1["all_cells_dff_df"],

            os.path.join(
                OUTPUT_DIR,
                "all_cells_dff.png"
            ),
            "All Cells"
        )

        plot_dff_traces(

            profiler1["active_cells_dff_df"],

            os.path.join(
                OUTPUT_DIR,
                "active_cells_dff.png"
            ),
            "Active Cells"
        )

    except FileNotFoundError as e:

        print(
            f"File not found: {e}"
        )

    except Exception as e:

        print(
            f"Unexpected error: {e}"
        )

    print("\nProfiler1")

    print(
        profiler1["all_cells_dff_df"].shape
    )

    print(
        profiler1["active_cells_dff_df"].shape
    )

    print(
        profiler1["summary"].head()
    )

    print("\nProfiler2")

    print(
        len(profiler2)
    )

if __name__ == "__main__":
    main()