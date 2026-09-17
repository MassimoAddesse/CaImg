from PySide6.QtCore import QObject, Signal, Slot
from config.analysis_config import AnalysisConfig
from src.pipeline import CaImgPipeline
from src.detection.adaptive_std import AdaptiveSTDDetector
from src.detection.adaptive_mad import AdaptiveMADDetector
from src.detection.sg_prominence import SGProminenceDetector
from pathlib import Path

class AnalysisWorker(QObject):
    """
    Runs the CaImg analysis pipeline outside the GUI thread.

    This prevents the Qt interface from freezing while Cellpose,
    fluorescence extraction, event detection, etc. are running.
    """

    finished = Signal(object)
    error = Signal(str)
    status = Signal(str)
    detail = Signal(str)

    progress = Signal(int)

    def __init__(self, tiff_path, method, frame_rate):

        super().__init__()

        self.tiff_path = tiff_path
        self.method = method
        self.frame_rate = frame_rate


    def create_detector(self, config):

        if self.method == "Adaptive STD":
            return AdaptiveSTDDetector(
                config.detection
            )

        elif self.method == "Adaptive MAD":
            return AdaptiveMADDetector(
                config.detection
            )

        elif self.method == "SG + Prominence":
            return SGProminenceDetector(
                config.detection
            )

        raise ValueError(
            f"Unknown detection method: {self.method}"
        )
    
    @Slot()
    def run(self):

        try:

            self.progress.emit(0)

            self.status.emit(
                "Preparing analysis"
            )

            self.detail.emit(
                "Initializing CaImg Analyzer..."
            )

            config = AnalysisConfig()

            config.recording.frame_rate = (
                self.frame_rate
            )

            self.progress.emit(5)

            self.status.emit(
                "Event detection"
            )

            self.detail.emit(
                f"Selected method: {self.method}"
            )

            detector = self.create_detector(
                config
            )

            pipeline = CaImgPipeline(
                config
            )

            self.progress.emit(10)

            self.status.emit(
                "Loading recording"
            )

            self.detail.emit(
                f"Loading {Path(self.tiff_path).name}..."
            )

            pipeline.load_data(
                self.tiff_path
            )

            self.detail.emit(
                "Recording loaded successfully."
            )

            self.progress.emit(20)

            self.status.emit(
                "Cell segmentation"
            )

            self.detail.emit(
                "Running Cellpose..."
            )

            pipeline.segment_cells()

            try:

                n_cells = len(
                    pipeline.masks
                )

                self.detail.emit(
                    f"Found {n_cells} cells."
                )

            except Exception:

                self.detail.emit(
                    "Cell segmentation completed."
                )

            self.progress.emit(35)

            self.status.emit(
                "Fluorescence extraction"
            )

            self.detail.emit(
                "Extracting fluorescence from cells..."
            )

            pipeline.extract_fluorescence()

            try:

                n_cells = len(
                    pipeline.fluorescence.columns
                )

                self.detail.emit(
                    f"Fluorescence extracted for "
                    f"{n_cells} cells."
                )

            except Exception:

                self.detail.emit(
                    "Fluorescence extraction completed."
                )

            self.progress.emit(45)


            self.status.emit(
                "ΔF/F calculation"
            )

            self.detail.emit(
                "Calculating fluorescence baseline "
                "and ΔF/F..."
            )

            pipeline.normalize()

            self.detail.emit(
                "ΔF/F calculation completed."
            )

            self.progress.emit(55)

            self.status.emit(
                "Event detection"
            )

            self.detail.emit(
                f"Detecting events using "
                f"{self.method}..."
            )

            pipeline.detect_events(
                detector
            )

            try:

                total_events = sum(
                    len(result.events)
                    for result
                    in pipeline.detection_results.values()
                )

                self.detail.emit(
                    f"Detected {total_events} events."
                )

            except Exception:

                self.detail.emit(
                    "Event detection completed."
                )

            self.progress.emit(70)

            self.status.emit(
                "Event metrics"
            )

            self.detail.emit(
                "Calculating event-level metrics..."
            )

            pipeline.calculate_event_metrics()

            self.detail.emit(
                "Event metrics calculated."
            )

            self.progress.emit(85)

            self.status.emit(
                "Cell and population analysis"
            )

            self.detail.emit(
                "Calculating single-cell and "
                "population metrics..."
            )

            pipeline.calculate_cell_and_population_metrics()

            self.detail.emit(
                "Cell and population metrics calculated."
            )

            self.progress.emit(95)

            self.status.emit(
                "Finalizing results"
            )

            self.detail.emit(
                "Preparing analysis results..."
            )

            results = pipeline.get_results()

            self.progress.emit(100)

            self.status.emit(
                "Analysis completed"
            )

            self.detail.emit(
                "Analysis completed successfully."
            )

            self.finished.emit(
                results
            )

        except Exception as exc:

            self.error.emit(
                f"{type(exc).__name__}: {exc}"
            )

            