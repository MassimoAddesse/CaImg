from dataio.excel_loader import load_fluorescence
from dataio.controls_loader import load_controls
from dataio.exporter import export_events
from analysis.compute_threshold import compute_threshold
from pipeline import CalciumAnalysis
from models import AnalysisConfig
from dataio.plotting import plot_dff_traces, plot_detected_events
import os
import time

INPUT_FILE = r"d:\ROIs\Fox\Foxg1 1.csv"
CONTROLS_DIR = r"D:\ROIs\Controls"
OUTPUT_DIR = r"results"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

def main():
    
    start_time = time.perf_counter()

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

        elapsed_time = (
            time.perf_counter() - start_time    
        )

        print(
            f"Analysis completed in {elapsed_time:.3f} seconds"
        )

        profiler1 = results[
            "profiler1"
        ]

        profiler2 = results[
            "profiler2"
        ]

        profiler3 = results[
            "profiler3"
        ]

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

        profiler3["correlation_matrix"].to_excel(
            os.path.join(
                OUTPUT_DIR,
                "profiler3_correlation_matrix.xlsx"
            )
        )

        profiler3["cell_summary"].to_excel(
            os.path.join(
                OUTPUT_DIR,
                "profiler3_cell_summary.xlsx"
            ),
            index=False
        )

        profiler3["correlation_distribution"].to_excel(
            os.path.join(
                OUTPUT_DIR,
                "profiler3_correlation_distribution.xlsx"
            ),
            index=False
        )

        profiler3["network_summary"].to_excel(
            os.path.join(
                OUTPUT_DIR,
                "profiler3_network_summary.xlsx"
            ),
            index=False
        )

        profiler3["renorm_df"].to_excel(
            os.path.join(
                OUTPUT_DIR,
                "profiler3_renorm_df.xlsx"
            )
        )


    except FileNotFoundError as e:

        print(
            f"File not found: {e}"
        )

    except Exception as e:

        print(
            f"Unexpected error: {e}"
        )

        return

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

    print(
        
        profiler1["summary"]["Events"].describe()
        
    )
    
    print(
        profiler1["summary"]
        .sort_values(
            "Events",
            ascending=True
        )
        .head(20)
    )

    for cell_name in profiler1["active_cells"][:10]:

        plot_detected_events(
            profiler1["active_cells_dff_df"],
            profiler1["events"][cell_name],
            config.threshold,
            cell_name,
            f"results/debug_{cell_name}_events.png"
        )
if __name__ == "__main__":
    main()