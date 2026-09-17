from .base import DetectionResult, EventDetector
from .global_threshold import GlobalThresholdDetector
from .adaptive_std import AdaptiveSTDDetector
from .adaptive_mad import AdaptiveMADDetector
from .sg_prominence import SGProminenceDetector

__all__ = [
    "DetectionResult",
    "EventDetector",
    "GlobalThresholdDetector",
    "AdaptiveSTDDetector",
    "AdaptiveMADDetector",
    "SGProminenceDetector",
]