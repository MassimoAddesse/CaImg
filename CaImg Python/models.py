from dataclasses import dataclass

@dataclass
class Event:
    
    cell_id: str

    start_frame: int
    end_frame: int

    peak: float
    integral: float

    rise_time: float
    decay_time: float

    rise_speed: float
    decay_speed: float

    event_std: float

    @property
    def duration(self) -> int:

        return(
            self.end_frame
            - self.start_frame
            + 1
        )

@dataclass
class AnalysisConfig:

    threshold: float | None = None

    threshold_factor: float = 4

    half_window: int = 20

    rise_fraction: float = 0.9

    decay_fraction: float = 0.9

    edge_margin: int = 50

    def __post_init__(self):

        if self.threshold is not None and self.threshold <= 0:
            raise ValueError(
                "threshold must be positive"
            )

        if self.threshold_factor <= 0:
            raise ValueError(
                "threshold_factor must be positive"
            )

        if self.half_window <= 0:
            raise ValueError(
                "half_window must be positive"
            )

        if not 0 < self.rise_fraction <= 1:
            raise ValueError(
                "rise_fraction must be between 0 and 1"
            )

        if not 0 < self.decay_fraction <= 1:
            raise ValueError(
                "decay_fraction must be between 0 and 1"
            )

@dataclass
class CellProfile:

    cell_id: int

    mean_fluo: float

    median_fluo: float

    std_fluo: float

    max_fluo: float

    min_fluo: float

    active: bool