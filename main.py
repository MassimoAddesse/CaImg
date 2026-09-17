from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config.analysis_config import AnalysisConfig

from pipeline import CaImgPipeline

from detection.adaptive_std import AdaptiveSTDDetector
from detection.adaptive_mad import AdaptiveMADDetector
from detection.sg_prominence import SGProminenceDetector

from dataio.exporter import export_results


def create_detector(
        method: str,
        config: AnalysisConfig
):
    """
    Create the detector selected in the GUI.

    Parameters
    ----------
    method : str
        Detection method selected by the user.

    config : AnalysisConfig
        Complete analysis configuration.

    Returns
    -------
    EventDetector
        Configured detector object.
    """

    if method == "Adaptive STD":
        return AdaptiveSTDDetector(
            config.detection
        )

    if method == "Adaptive MAD":
        return AdaptiveMADDetector(
            config.detection
        )

    if method == "SG + Prominence":
        return SGProminenceDetector(
            config.detection
        )

    raise ValueError(
        f"Unknown detection method: {method}"
    )


class CaImgGUI:
    """
    Simple graphical interface for CaImg Analyzer.

    The GUI allows the user to:
    - select a TIFF recording;
    - select the detection method;
    - select an output folder;
    - start the analysis.
    """

    def __init__(
            self,
            root: tk.Tk
    ):

        self.root = root

        self.root.title(
            "CaImg Analyzer"
        )

        self.root.geometry(
            "600x400"
        )

        self.root.resizable(
            False,
            False
        )

        self.tiff_path = None
        self.output_folder = None

        self._build_gui()

    def _build_gui(self):
        """
        Build the graphical interface.
        """

        main_frame = ttk.Frame(
            self.root,
            padding=25
        )

        main_frame.pack(
            fill="both",
            expand=True
        )

        title = ttk.Label(
            main_frame,
            text="CaImg Analyzer",
            font=("TkDefaultFont", 20, "bold")
        )

        title.pack(
            pady=(0, 25)
        )

        tiff_frame = ttk.Frame(
            main_frame
        )

        tiff_frame.pack(
            fill="x",
            pady=8
        )

        ttk.Label(
            tiff_frame,
            text="TIFF file:"
        ).pack(
            side="left"
        )

        self.tiff_label = ttk.Label(
            tiff_frame,
            text="No file selected",
            width=45
        )

        self.tiff_label.pack(
            side="left",
            padx=10
        )

        ttk.Button(
            tiff_frame,
            text="Choose file...",
            command=self.choose_tiff
        ).pack(
            side="right"
        )

        method_frame = ttk.Frame(
            main_frame
        )

        method_frame.pack(
            fill="x",
            pady=15
        )

        ttk.Label(
            method_frame,
            text="Detection method:"
        ).pack(
            side="left"
        )

        self.method_var = tk.StringVar(
            value="Adaptive STD"
        )

        self.method_menu = ttk.Combobox(
            method_frame,
            textvariable=self.method_var,
            values=[
                "Adaptive STD",
                "Adaptive MAD",
                "SG + Prominence"
            ],
            state="readonly",
            width=30
        )

        self.method_menu.pack(
            side="right"
        )

        output_frame = ttk.Frame(
            main_frame
        )

        output_frame.pack(
            fill="x",
            pady=8
        )

        ttk.Label(
            output_frame,
            text="Save results in:"
        ).pack(
            side="left"
        )

        self.output_label = ttk.Label(
            output_frame,
            text="No folder selected",
            width=45
        )

        self.output_label.pack(
            side="left",
            padx=10
        )

        ttk.Button(
            output_frame,
            text="Choose folder...",
            command=self.choose_output_folder
        ).pack(
            side="right"
        )

        self.analyze_button = ttk.Button(
            main_frame,
            text="ANALYZE",
            command=self.run_analysis
        )

        self.analyze_button.pack(
            pady=(30, 15),
            ipadx=30,
            ipady=8
        )

        self.status_var = tk.StringVar(
            value="Ready"
        )

        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var
        )

        self.status_label.pack(
            pady=5
        )

    def choose_tiff(self):
        """
        Open a file-selection dialog for the TIFF recording.
        """

        path = filedialog.askopenfilename(
            title="Select TIFF recording",
            filetypes=[
                (
                    "TIFF files",
                    "*.tif *.tiff"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not path:
            return

        self.tiff_path = Path(
            path
        )

        self.tiff_label.config(
            text=self.tiff_path.name
        )

        self.status_var.set(
            "TIFF file selected."
        )

    def choose_output_folder(self):
        """
        Open a folder-selection dialog for the output directory.
        """

        folder = filedialog.askdirectory(
            title="Select output folder"
        )

        if not folder:
            return

        self.output_folder = Path(
            folder
        )

        self.output_label.config(
            text=str(self.output_folder)
        )

        self.status_var.set(
            "Output folder selected."
        )

    def run_analysis(self):
        """
        Run the complete CaImg Analyzer pipeline.
        """

        if self.tiff_path is None:

            messagebox.showwarning(
                "Missing TIFF file",
                "Please select a TIFF recording first."
            )

            return

        if self.output_folder is None:

            messagebox.showwarning(
                "Missing output folder",
                "Please select a folder for saving the results."
            )

            return

        try:

            self.analyze_button.config(
                state="disabled"
            )

            self.status_var.set(
                "Running analysis..."
            )

            self.root.update_idletasks()

            config = AnalysisConfig()

            detector = create_detector(
                method=self.method_var.get(),
                config=config
            )

            pipeline = CaImgPipeline(
                config=config
            )

            pipeline.run(
                tiff_path=self.tiff_path,
                detector=detector
            )

            results = pipeline.get_results()

            output_path = (
                self.output_folder
                / f"{self.tiff_path.stem}_results.xlsx"
            )

            export_results(
                results=results,
                output_path=output_path
            )

            self.status_var.set(
                "Analysis completed successfully."
            )

            messagebox.showinfo(
                "Analysis complete",
                "Analysis completed successfully.\n\n"
                f"Results saved to:\n{output_path}"
            )

        except Exception as error:

            self.status_var.set(
                "Analysis failed."
            )

            messagebox.showerror(
                "Analysis error",
                f"An error occurred during the analysis:\n\n{error}"
            )

        finally:

            self.analyze_button.config(
                state="normal"
            )

def main():
    """
    Start the CaImg Analyzer graphical interface.
    """

    root = tk.Tk()

    CaImgGUI(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()
