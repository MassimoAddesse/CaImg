from dataclasses import dataclass, field

@dataclass
class RecordingConfig:

    frame_rate: float = 4.0

@dataclass
class SegmentationConfig:

    cellpose_diameter: float = 30.0
    use_gpu: bool = True

@dataclass
class DFFConfig:

    half_window: int = 20
    edge_margin: int = 49
    eps: float = 1e-12

@dataclass
class DetectionConfig:

    std_k_high: float = 4.0
    std_k_low: float = 2.0

    mad_k_high: float = 3.5
    mad_k_low: float = 1.0

    sg_window: int = 11
    sg_polyorder: int = 3

    prominence_k: float = 6.0 

    min_event_duration: int = 2
    min_peak_distance: int = 5

    use_hysteresis: bool = True

@dataclass
class AnalysisConfig:

    recording: RecordingConfig = field(
        default_factory= RecordingConfig
    )
    segmentation: SegmentationConfig = field(
        default_factory = SegmentationConfig
    )
    dff: DFFConfig = field(
        default_factory = DFFConfig
    )
    detection: DetectionConfig = field(
        default_factory = DetectionConfig
    )

    
