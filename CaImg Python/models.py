from dataclasses import dataclass

@dataclass
class Event:
    
    cell_id: int

    start_frame: int
    end_frame: int

    peak: float
    integral: float

    rise_time: float
    decay_time: float

    rise_speed: float
    decay_speed: float

    @property
    def duration(self):

        return(
            self.end_frame
            - self.start_frame
            + 1
        )

@dataclass
class AnalysisConfig:

    threshold: float | None = None

    threshold_factor: float = 3

    half_window: int = 20

    rise_fraction: float = 0.9

    decay_fraction: float = 0.9

@dataclass
class CellProfile:

    cell_id: int

    mean_fluo: float

    mediam_fluo: float

    std_fluo: float

    max_fluo: float

    min_fluo: float

    active: bool