"""
    Contourify — Turn any image into an interactive SVG
    with AI-powered object detection and clickable hotspots.
 
    Basic usage:
        from contourify import Contourify
 
        ct = Contourify()
        objects = ct.detect("image.jpg")
        svg = ct.generate(
            image_path="image.jpg",
            object_id=0,
            text="My Product",
            link="https://example.com",
        )
        with open("output.svg", "w") as f:
            f.write(svg)
 
    Using a custom detector:
        from contourify import Contourify
        from contourify.adapters import BaseDetector
 
        class MyDetector(BaseDetector):
            def detect(self, image_path, **kwargs):
                # your model here
                return [...]
 
        ct = Contourify(detector=MyDetector())
 
    Using a larger YOLO model:
        ct = Contourify(model="yolov8s-seg.pt")
"""
 
__version__ = "0.2.0"
__author__  = "Victor Chukwuemeka"
__email__   = "onwuegbuchulemvic02@gmail.com"
__license__ = "MIT"
 
from contourify.core.detector  import Detector, DetectedObject, BBox
from contourify.core.generator import Generator
from contourify.core.validator import validate_image
from contourify.adapters.base  import BaseDetector
from contourify.adapters.yolo  import YOLODetector
 
 
class Contourify:
    """
    Main entry point for the contourify library.
 
    Example:
        ct = Contourify()
 
        # Detect objects
        objects = ct.detect("photo.jpg")
 
        # Generate interactive SVG
        svg = ct.generate(
            image_path="photo.jpg",
            object_id=0,
            text="Click me",
            link="https://example.com",
            color="#3b82f6",
        )
 
        # Override misdetected label
        svg = ct.generate(
            image_path="photo.jpg",
            object_id=0,
            text="Beautiful Fallow Deer",
            link="https://example.com",
            label="Deer",
        )
 
        # Generate HTML wrapper — no white space when opened locally
        html = ct.generate(
            image_path="photo.jpg",
            object_id=0,
            text="My Product",
            link="https://example.com",
            fmt="html",
        )
 
        # Use a custom detector
        from contourify.adapters import BaseDetector
        ct = Contourify(detector=MyCustomDetector())
 
        # Use a larger YOLO model for better accuracy
        ct = Contourify(model="yolov8s-seg.pt")
    """
 
    def __init__(
        self,
        model:    str | None          = None,
        detector: BaseDetector | None = None,
    ):
        """
        Initialise Contourify.
 
        Args:
            model:    YOLOv8 model name or path to a .pt file.
                      Ignored if detector is provided.
                      Defaults to yolov8n-seg.pt.
            detector: Custom detector instance implementing BaseDetector.
                      If provided, model parameter is ignored.
                      This allows plugging in TensorFlow, custom models
                      or any other detection backend.
        """
        if detector is not None:
            if not isinstance(detector, BaseDetector):
                raise TypeError(
                    "detector must be an instance of BaseDetector. "
                    "See contourify.adapters.BaseDetector."
                )
            self._detector = detector
        else:
            self._detector = YOLODetector(
                model=model or "yolov8n-seg.pt"
            )
 
        self._generator = Generator()
 
    def detect(self, image_path: str) -> list:
        """
        Detect all objects in an image.
 
        Args:
            image_path: Path to the image file.
 
        Returns:
            List of DetectedObject instances with id, label,
            score, bbox and contour attributes.
 
        Raises:
            FileNotFoundError: If the image does not exist.
            ValueError: If the image fails quality validation.
        """
        valid, reason = validate_image(image_path)
        if not valid:
            raise ValueError(reason)
        return self._detector.detect(image_path)
 
    def generate(
        self,
        image_path: str,
        object_id:  int,
        text:       str,
        link:       str,
        color:      str = "#3b82f6",
        label:      str | None = None,
        fmt:        str = "svg",
    ) -> str:
        """
        Generate an interactive SVG or HTML for a detected object.
 
        Args:
            image_path: Path to the image file.
            object_id:  ID of the detected object to annotate.
            text:       Description text shown in the hover popup.
            link:       URL opened when the user clicks Visit Link.
            color:      Highlight color as a hex string.
                        Defaults to blue (#3b82f6).
            label:      Override the label shown in the popup header.
                        Useful when the detector misidentifies an object.
                        If None the detected label is used.
            fmt:        Output format. "svg" (default) or "html".
                        Use "html" to eliminate white space when
                        opening the file locally in a browser.
 
        Returns:
            SVG or HTML document as a string.
 
        Raises:
            FileNotFoundError: If the image does not exist.
            ValueError: If the object_id is not found or fmt is invalid.
        """
        if fmt not in ("svg", "html"):
            raise ValueError(
                f"Invalid format '{fmt}'. Use 'svg' or 'html'."
            )
 
        valid, reason = validate_image(image_path)
        if not valid:
            raise ValueError(reason)
 
        objects = self._detector.detect(image_path)
        obj = next((o for o in objects if o.id == object_id), None)
        if obj is None:
            raise ValueError(
                f"Object with id {object_id} not found. "
                f"Available ids: {[o.id for o in objects]}"
            )
 
        svg = self._generator.generate(
            image_path=image_path,
            obj=obj,
            text=text,
            link=link,
            color=color,
            label=label,
        )
 
        if fmt == "html":
            return self._generator.wrap_html(svg)
 
        return svg
 
    def detect_and_generate(
        self,
        image_path: str,
        object_id:  int,
        text:       str,
        link:       str,
        color:      str = "#3b82f6",
        label:      str | None = None,
        fmt:        str = "svg",
    ) -> tuple[list, str]:
        """
        Convenience method — detect and generate in one call.
 
        Returns:
            Tuple of (objects, output_string).
        """
        valid, reason = validate_image(image_path)
        if not valid:
            raise ValueError(reason)
 
        objects = self._detector.detect(image_path)
        obj = next((o for o in objects if o.id == object_id), None)
        if obj is None:
            raise ValueError(
                f"Object with id {object_id} not found. "
                f"Available ids: {[o.id for o in objects]}"
            )
 
        svg = self._generator.generate(
            image_path=image_path,
            obj=obj,
            text=text,
            link=link,
            color=color,
            label=label,
        )
 
        output = self._generator.wrap_html(svg) if fmt == "html" else svg
        return objects, output
 
 
__all__ = [
    "Contourify",
    "Detector",
    "DetectedObject",
    "BBox",
    "Generator",
    "BaseDetector",
    "YOLODetector",
    "validate_image",
    "__version__",
]
 