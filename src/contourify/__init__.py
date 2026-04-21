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
"""

__version__ = "0.1.0"
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
    """

    def __init__(self, model: str = "yolov8n-seg.pt"):
        """
        Initialise Contourify.

        Args:
            model: YOLOv8 segmentation model name or path.
                   Defaults to yolov8n-seg.pt (auto-downloaded on first use).
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
    ) -> str:
        """
        Generate an interactive SVG for a detected object.

        Args:
            image_path: Path to the image file.
            object_id:  ID of the detected object to annotate.
            text:       Description text shown in the hover popup.
            link:       URL opened when the user clicks Visit Link.
            color:      Highlight color as a hex string.
                        Defaults to blue (#3b82f6).

        Returns:
            SVG document as a string.

        Raises:
            FileNotFoundError: If the image does not exist.
            ValueError: If the object_id is not found.
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

        return self._generator.generate(
            image_path=image_path,
            obj=obj,
            text=text,
            link=link,
            color=color,
        )

    def detect_and_generate(
        self,
        image_path: str,
        object_id:  int,
        text:       str,
        link:       str,
        color:      str = "#3b82f6",
    ) -> tuple[list, str]:
        """
        Convenience method — detect and generate in one call.

        Returns:
            Tuple of (objects, svg_string).
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
        )
        return objects, svg


__all__ = [
    "Contourify",
    "Detector",
    "Generator",
    "validate_image",
    "__version__",
]