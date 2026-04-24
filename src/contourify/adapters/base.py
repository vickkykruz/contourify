"""
    Base detector interface.
 
    Defines the contract that all detection adapters must follow.
    Any detection backend — YOLO, TensorFlow, custom — that
    implements this interface works seamlessly with contourify.
 
    Example — implementing a custom detector:
 
        from contourify.adapters.base import BaseDetector
        from contourify.core.detector import DetectedObject, BBox
 
        class MyCustomDetector(BaseDetector):
 
            def detect(self, image_path: str, **kwargs) -> list:
                # Run your model here
                # Return list of DetectedObject instances
                return [
                    DetectedObject(
                        id=0,
                        label="my_object",
                        score=0.95,
                        bbox=BBox(x1=0.1, y1=0.1, x2=0.9, y2=0.9),
                        contour=[[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]],
                        width=640,
                        height=480,
                    )
                ]
 
        # Use with Contourify
        from contourify import Contourify
        ct = Contourify(detector=MyCustomDetector())
"""
 
from __future__ import annotations
 
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING
 
if TYPE_CHECKING:
    from contourify.core.detector import DetectedObject
 
 
class BaseDetector(ABC):
    """
    Abstract base class for all contourify detection adapters.
 
    To create a custom detector:
        1. Subclass BaseDetector
        2. Implement the detect() method
        3. Return a list of DetectedObject instances
        4. Pass your detector to Contourify(detector=your_detector)
 
    The DetectionResult contract:
        - Each DetectedObject must have id, label, score, bbox, contour
        - bbox values must be normalised (0-1 range)
        - contour points must be normalised (0-1 range)
        - width and height must be the natural image dimensions in pixels
    """
 
    @abstractmethod
    def detect(
        self,
        image_path: str,
        **kwargs,
    ) -> List["DetectedObject"]:
        """
        Detect objects in an image.
 
        Args:
            image_path: Absolute path to the image file.
            **kwargs:   Additional model-specific parameters.
 
        Returns:
            List of DetectedObject instances. Empty list if
            no objects are detected. Must be sorted by
            confidence score descending.
 
        Raises:
            FileNotFoundError: If the image does not exist.
            RuntimeError:      If inference fails.
        """
        ...
 
    @property
    def name(self) -> str:
        """
        Human-readable name of this detector.
        Override in subclasses for better CLI output.
        """
        return self.__class__.__name__
 