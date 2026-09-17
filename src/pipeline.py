from pathlib import Path
import pandas as pd
from config.analysis_config import AnalysisConfig
from dataio.tiff_loader import load_tiff
from segmentation.cellpose import segment_cells
from fluorescence.extraction import extract_fluorescence
from fluorescence.normalization import calculate_dff_dataframe
from detection.runner import detect_all_cells
from metrics.runner import profile_all_cells
from analysis.analysis_runner import run_analysis


class CaImgPipeline:
    """
    Main analysis pipeline for CaImg Analyzer.

    The pipeline coordinates the different stages of the analysis.
    Individual scientific algorithms remain inside their respective
    modules.

    Parameters
    ----------
    config : AnalysisConfig
        Configuration containing recording, segmentation, DFF,
        and detection parameters.

    Returns
    -------
    CaImgPipeline
        Pipeline object containing the analysis results.
    """

    def __init__(
            self,
            config
    ):

        self.config = config

        self.tiff_path = None

        self.stack = None

        self.masks = None

        self.fluorescence = None

        self.f0 = None

        self.dff = None

        self.detection_results = None

        self.profiles = None

        self.analysis_results = None

    def load_data(
            self,
            tiff_path: str | Path
    ):
        """
        Load the TIFF recording.

        Parameters
        ----------
        tiff_path : str or pathlib.Path
            Path to the TIFF recording.

        Returns
        -------
        CaImgPipeline
            Current pipeline object.
        """

        self.tiff_path = Path(
            tiff_path
        )

        if not self.tiff_path.exists():
            raise FileNotFoundError(
                f"TIFF file not found: {self.tiff_path}"
            )

        self.stack = load_tiff(
            str(self.tiff_path)
        )

        return self

    def segment_cells(self):
        """
        Segment cells using the configured Cellpose parameters.

        Returns
        -------
        CaImgPipeline
            Current pipeline object.
        """

        if self.stack is None:
            raise RuntimeError(
                "Data must be loaded before segmentation."
            )

        self.masks = segment_cells(
            stack=self.stack,
            diameter=(
                self.config.segmentation.cellpose_diameter
            ),
            use_gpu=(
                self.config.segmentation.use_gpu
            )
        )

        return self


    def extract_fluorescence(self):
        """
        Extract mean fluorescence for every ROI.

        Returns
        -------
        CaImgPipeline
            Current pipeline object.
        """

        if self.stack is None:
            raise RuntimeError(
                "Data must be loaded before fluorescence extraction."
            )

        if self.masks is None:
            raise RuntimeError(
                "Cells must be segmented before fluorescence extraction."
            )

        self.fluorescence = extract_fluorescence(
            self.stack,
            self.masks
        )

        return self

    def normalize(self):
        """
        Calculate F0 and dF/F0 for every ROI.

        Returns
        -------
        CaImgPipeline
            Current pipeline object.
        """

        if self.fluorescence is None:
            raise RuntimeError(
                "Fluorescence must be extracted before normalization."
            )

        self.dff, self.f0 = calculate_dff_dataframe(
            fluorescence=self.fluorescence,
            config=self.config.dff
        )

        return self


    def detect_events(
            self,
            detector
    ):
        """
        Detect calcium events independently for every ROI.

        Parameters
        ----------
        detector : EventDetector
            Detector instance selected for the analysis.

        Returns
        -------
        CaImgPipeline
            Current pipeline object.
        """

        if self.dff is None:
            raise RuntimeError(
                "DFF must be calculated before event detection."
            )

        self.detection_results = detect_all_cells(
            dff_df=self.dff,
            detector=detector
        )

        return self

    def calculate_event_metrics(self):
        """
        Calculate event-based metrics for every detected event.

        Returns
        -------
        CaImgPipeline
            Current pipeline object.
        """

        if self.dff is None:
            raise RuntimeError(
                "DFF must be calculated before event metrics."
            )

        if self.detection_results is None:
            raise RuntimeError(
                "Events must be detected before event metrics."
            )

        self.profiles = profile_all_cells(
            dff_df=self.dff,
            detection_results=self.detection_results,
            sampling_rate=self.config.recording.frame_rate
        )

        return self

    def calculate_cell_and_population_metrics(self):
        """
        Calculate cell-level and population-level analysis.

        Returns
        -------
        CaImgPipeline
            Current pipeline object.
        """

        if self.dff is None:
            raise RuntimeError(
                "DFF must be calculated before downstream analysis."
            )

        if self.profiles is None:
            raise RuntimeError(
                "Event profiles must be calculated before downstream analysis."
            )

        recording_duration = (
            len(self.dff)
            / self.config.recording.frame_rate
        )

        self.analysis_results = run_analysis(
            dff_df=self.dff,
            profiles=self.profiles,
            recording_duration=recording_duration,
            sampling_rate=self.config.recording.frame_rate
        )

        return self

    def run_analysis(
            self,
            detector
    ):
        """
        Run the complete CaImg Analyzer pipeline.

        Parameters
        ----------
        detector : EventDetector
            Detection method selected by the user.

        Returns
        -------
        CaImgPipeline
            Current pipeline object containing the analysis results.
        """

        self.load_data(
            self.tiff_path
        )

        self.segment_cells()
        self.extract_fluorescence()
        self.normalize()
        self.detect_events(detector)
        self.calculate_event_metrics()
        self.calculate_cell_and_population_metrics()

        return self

    def run(
            self,
            tiff_path: str | Path,
            detector
    ):
        """
        Load a recording and run the complete analysis.

        Parameters
        ----------
        tiff_path : str or pathlib.Path
            Path to the TIFF recording.

        detector : EventDetector
            Detection method selected by the user.

        Returns
        -------
        CaImgPipeline
            Completed pipeline.
        """

        self.load_data(
            tiff_path
        )

        self.segment_cells()
        self.extract_fluorescence()
        self.normalize()
        self.detect_events(detector)
        self.calculate_event_metrics()
        self.calculate_cell_and_population_metrics()

        return self

    def get_results(
            self
    ) -> dict:
        """
        Return all available analysis results.

        Returns
        -------
        dict
            Dictionary containing intermediate and final results.
        """

        return {
            "fluorescence": self.fluorescence,
            "f0": self.f0,
            "dff": self.dff,
            "detection_results": self.detection_results,
            "profiles": self.profiles,
            "analysis": self.analysis_results,
        }
