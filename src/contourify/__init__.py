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
 
        # Generate HTML wrapper (fixes white space when opening locally)
        html = ct.generate(
            image_path="image.jpg",
            object_id=0,
            text="My Product",
            link="https://example.com",
            fmt="html",
        )
        with open("output.html", "w") as f:
            f.write(html)
"""
 
__version__ = "0.1.2"
__author__  = "Victor Chukwuemeka"
__email__   = "onwuegbuchulemvic02@gmail.com"
__license__ = "MIT"
 
from contourify.core.detector  import Detector
from contourify.core.generator import Generator
from contourify.core.validator import validate_image
 
 
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
    """
 
    def __init__(self, model: str = "yolov8n-seg.pt"):
        """
        Initialise Contourify.
 
        Args:
            model: YOLOv8 segmentation model name or path.
                   Defaults to yolov8n-seg.pt (auto-downloaded
                   to ~/.contourify/models/ on first use).
        """
        self._detector  = Detector(model=model)
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
                        Useful when YOLO misidentifies an object.
                        If None the YOLO detected label is used.
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
 
        Args:
            image_path: Path to the image file.
            object_id:  ID of the detected object to annotate.
            text:       Description text shown in the hover popup.
            link:       URL opened when the user clicks Visit Link.
            color:      Highlight color as a hex string.
            label:      Override the label shown in the popup header.
            fmt:        Output format. "svg" or "html".
 
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
    "Generator",
    "validate_image",
    "__version__",
]
 