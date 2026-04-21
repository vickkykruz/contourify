"""
    Tests for image quality validator.
"""

import os
import random
import pytest
from PIL import Image

from contourify.core.validator import validate_image, get_image_dimensions


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_image(
    width: int,
    height: int,
    tmp_path: str,
    noisy: bool = True,
) -> str:
    """
    Create a temporary test image.

    Args:
        width:    Image width in pixels.
        height:   Image height in pixels.
        tmp_path: Directory to save the image.
        noisy:    If True adds random pixel noise to increase
                  file size above the 20KB minimum threshold.
    """
    filepath = os.path.join(tmp_path, f"test_{width}x{height}.jpg")
    img = Image.new("RGB", (width, height), color=(100, 150, 200))

    if noisy:
        # Add random noise so JPEG compression produces a
        # realistically-sized file above the 20KB threshold
        pixels = img.load()
        for y in range(height):
            for x in range(width):
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                pixels[x, y] = (r, g, b)

    img.save(filepath, "JPEG", quality=95)
    return filepath


# ── validate_image tests ──────────────────────────────────────────────────────

class TestValidateImage:

    def test_valid_image_passes(self, tmp_path):
        """A clear, high-resolution noisy image should pass."""
        filepath = make_image(800, 600, str(tmp_path))
        valid, reason = validate_image(filepath)
        assert valid is True
        assert reason == ""

    def test_file_not_found(self):
        """Non-existent file should fail."""
        valid, reason = validate_image("/nonexistent/path/image.jpg")
        assert valid is False
        assert "not found" in reason.lower()

    def test_resolution_too_low_width(self, tmp_path):
        """Image below minimum width should fail."""
        filepath = make_image(200, 400, str(tmp_path))
        valid, reason = validate_image(filepath)
        assert valid is False
        # Either file size or resolution check catches this
        assert reason != ""

    def test_resolution_too_low_height(self, tmp_path):
        """Image below minimum height should fail."""
        filepath = make_image(400, 200, str(tmp_path))
        valid, reason = validate_image(filepath)
        assert valid is False
        assert reason != ""

    def test_resolution_exactly_minimum_passes(self, tmp_path):
        """Image at exactly minimum resolution should pass."""
        filepath = make_image(300, 300, str(tmp_path))
        valid, reason = validate_image(filepath)
        assert valid is True

    def test_large_image_passes(self, tmp_path):
        """Large high-resolution image should pass."""
        filepath = make_image(1920, 1080, str(tmp_path))
        valid, reason = validate_image(filepath)
        assert valid is True

    def test_returns_tuple(self, tmp_path):
        """validate_image should always return a tuple."""
        filepath = make_image(800, 600, str(tmp_path))
        result = validate_image(filepath)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_valid_image_empty_reason(self, tmp_path):
        """Valid image should return empty reason string."""
        filepath = make_image(800, 600, str(tmp_path))
        valid, reason = validate_image(filepath)
        assert valid is True
        assert reason == ""

    def test_invalid_image_has_reason(self, tmp_path):
        """Invalid image should return non-empty reason string."""
        # Tiny image with no noise — fails file size check
        filepath = make_image(100, 100, str(tmp_path), noisy=False)
        valid, reason = validate_image(filepath)
        assert valid is False
        assert len(reason) > 0

    def test_boolean_return_type(self, tmp_path):
        """First element of tuple should always be bool."""
        filepath = make_image(800, 600, str(tmp_path))
        valid, _ = validate_image(filepath)
        assert isinstance(valid, bool)

    def test_reason_is_string(self, tmp_path):
        """Second element of tuple should always be string."""
        filepath = make_image(800, 600, str(tmp_path))
        _, reason = validate_image(filepath)
        assert isinstance(reason, str)


# ── get_image_dimensions tests ────────────────────────────────────────────────

class TestGetImageDimensions:

    def test_correct_dimensions(self, tmp_path):
        """Should return correct width and height."""
        filepath = make_image(640, 480, str(tmp_path))
        w, h = get_image_dimensions(filepath)
        assert w == 640
        assert h == 480

    def test_square_image(self, tmp_path):
        """Should handle square images correctly."""
        filepath = make_image(512, 512, str(tmp_path))
        w, h = get_image_dimensions(filepath)
        assert w == 512
        assert h == 512

    def test_file_not_found_raises(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            get_image_dimensions("/nonexistent/image.jpg")

    def test_returns_tuple(self, tmp_path):
        """Should return a tuple of two integers."""
        filepath = make_image(800, 600, str(tmp_path))
        result = get_image_dimensions(filepath)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)

    def test_wide_image(self, tmp_path):
        """Should handle wide landscape images."""
        filepath = make_image(1280, 720, str(tmp_path))
        w, h = get_image_dimensions(filepath)
        assert w == 1280
        assert h == 720

    def test_tall_image(self, tmp_path):
        """Should handle tall portrait images."""
        filepath = make_image(720, 1280, str(tmp_path))
        w, h = get_image_dimensions(filepath)
        assert w == 720
        assert h == 1280