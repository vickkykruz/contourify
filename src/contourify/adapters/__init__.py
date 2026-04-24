"""
    contourify detection adapters.
 
    Provides the BaseDetector interface and built-in adapters.
 
    Built-in adapters:
        YOLODetector   — YOLOv8 segmentation (default)
 
    To use a custom detector:
        from contourify.adapters import BaseDetector
        from contourify.core.detector import DetectedObject, BBox
 
        class MyDetector(BaseDetector):
            def detect(self, image_path: str, **kwargs) -> list:
                # your detection logic here
                return [DetectedObject(...)]
 
        from contourify import Contourify
        ct = Contourify(detector=MyDetector())
"""
 
from contourify.adapters.base import BaseDetector
from contourify.adapters.yolo import YOLODetector, YOLO_MODELS
 
__all__ = [
    "BaseDetector",
    "YOLODetector",
    "YOLO_MODELS",
]
 