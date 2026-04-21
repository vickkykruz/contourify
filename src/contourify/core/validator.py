"""
    Image quality validator.

    Validates images before processing to ensure they meet
    minimum quality requirements for accurate object detection.
"""

import os
from PIL import Image


# ── Quality thresholds ────────────────────────────────────────────────────────
MIN_WIDTH        = 300     # pixels
MIN_HEIGHT       = 300     # pixels
MIN_FILE_SIZE_KB = 20      # kilobytes
BLUR_THRESHOLD   = 80.0    # Laplacian variance


def validate_image(filepath: str) -> tuple[bool, str]:
    """
    Validate image quality before processing.

    Runs three checks in order:
        1. File exists
        2. Minimum file size
        3. Minimum resolution
        4. Blurriness via Laplacian variance

    Args:
        filepath: Path to the image file.

    Returns:
        (True, "")           if the image passes all checks.
        (False, reason_str)  if the image fails, with a clear reason.

    Example:
        valid, reason = validate_image("photo.jpg")
        if not valid:
            print(f"Image rejected: {reason}")
    """

    # 1. File exists
    if not os.path.exists(filepath):
        return False, f"File not found: {filepath}"

    # 2. File size
    file_size_kb = os.path.getsize(filepath) / 1024
    if file_size_kb < MIN_FILE_SIZE_KB:
        return False, (
            f"Image too small ({file_size_kb:.1f} KB). "
            f"Minimum is {MIN_FILE_SIZE_KB} KB."
        )

    # 3. Resolution
    try:
        with Image.open(filepath) as img:
            width, height = img.size
    except Exception as e:
        return False, f"Could not read image: {e}"

    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return False, (
            f"Resolution too low ({width}×{height}px). "
            f"Minimum is {MIN_WIDTH}×{MIN_HEIGHT}px."
        )

    # 4. Blurriness — Laplacian variance
    try:
        import cv2
        import numpy as np

        img_cv = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        if img_cv is not None:
            variance = cv2.Laplacian(img_cv, cv2.CV_64F).var()
            if variance < BLUR_THRESHOLD:
                return False, (
                    f"Image appears blurry (sharpness score: {variance:.1f}). "
                    "Please use a sharper, well-focused photo."
                )
    except ImportError:
        # opencv not available — skip blur check
        pass
    except Exception:
        # If blur check fails for any reason allow the image through
        pass

    return True, ""


def get_image_dimensions(filepath: str) -> tuple[int, int]:
    """
    Get image width and height.

    Args:
        filepath: Path to the image file.

    Returns:
        Tuple of (width, height) in pixels.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file cannot be opened as an image.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        with Image.open(filepath) as img:
            return img.size
    except Exception as e:
        raise ValueError(f"Could not read image dimensions: {e}")