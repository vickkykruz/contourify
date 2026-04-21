"""
    Tests for SVG generator.
"""

import os
import random
import pytest
from PIL import Image

from contourify.core.detector import DetectedObject, BBox
from contourify.core.generator import Generator


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_image(width: int, height: int, tmp_path: str) -> str:
    """Create a noisy test image above the file size threshold."""
    filepath = os.path.join(tmp_path, f"test_{width}x{height}.jpg")
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            pixels[x, y] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
    img.save(filepath, "JPEG", quality=95)
    return filepath


def make_detected_object(
    obj_id: int = 0,
    label: str = "chair",
    score: float = 0.91,
    img_w: int = 640,
    img_h: int = 480,
) -> DetectedObject:
    """Create a realistic DetectedObject for testing."""
    # Simple rectangular contour (normalized)
    contour = [
        [0.2, 0.2],
        [0.8, 0.2],
        [0.8, 0.8],
        [0.2, 0.8],
    ]
    bbox = BBox(x1=0.2, y1=0.2, x2=0.8, y2=0.8)
    return DetectedObject(
        id=obj_id,
        label=label,
        score=score,
        bbox=bbox,
        contour=contour,
        width=img_w,
        height=img_h,
    )


# ── Generator tests ───────────────────────────────────────────────────────────

class TestGenerator:

    def test_generate_returns_string(self, tmp_path):
        """generate() should return a string."""
        filepath = make_image(640, 480, str(tmp_path))
        obj      = make_detected_object(img_w=640, img_h=480)
        gen      = Generator()
        svg      = gen.generate(
            image_path=filepath,
            obj=obj,
            text="Test Chair",
            link="https://example.com",
        )
        assert isinstance(svg, str)

    def test_generate_is_valid_svg(self, tmp_path):
        """Output should start with SVG declaration."""
        filepath = make_image(640, 480, str(tmp_path))
        obj      = make_detected_object(img_w=640, img_h=480)
        gen      = Generator()
        svg      = gen.generate(
            image_path=filepath,
            obj=obj,
            text="Test Chair",
            link="https://example.com",
        )
        assert svg.strip().startswith("<?xml")
        assert "<svg" in svg
        assert "</svg>" in svg

    def test_generate_contains_image(self, tmp_path):
        """SVG should embed the image as base64."""
        filepath = make_image(640, 480, str(tmp_path))
        obj      = make_detected_object(img_w=640, img_h=480)
        gen      = Generator()
        svg      = gen.generate(
            image_path=filepath,
            obj=obj,
            text="Test",
            link="https://example.com",
        )
        assert "data:image/jpeg;base64," in svg

    def test_generate_contains_user_link(self, tmp_path):
        """SVG should contain the user's link."""
        filepath = make_image(640, 480, str(tmp_path))
        obj      = make_detected_object(img_w=640, img_h=480)
        gen      = Generator()
        svg      = gen.generate(
            image_path=filepath,
            obj=obj,
            text="Test",
            link="https://shop.example.com/chair",
        )
        assert "https://shop.example.com/chair" in svg

    def test_generate_contains_user_text(self, tmp_path):
        """SVG should contain the user's description text."""
        filepath = make_image(640, 480, str(tmp_path))
        obj      = make_detected_object(img_w=640, img_h=480)
        gen      = Generator()
        svg      = gen.generate(
            image_path=filepath,
            obj=obj,
            text="Handcrafted Oak Chair",
            link="https://example.com",
        )
        assert "Handcrafted Oak Chair" in svg

    def test_generate_contains_object_label(self, tmp_path):
        """SVG should contain the object label in uppercase."""
        filepath = make_image(640, 480, str(tmp_path))
        obj      = make_detected_object(label="laptop", img_w=640, img_h=480)
        gen      = Generator()
        svg      = gen.generate(
            image_path=filepath,
            obj=obj,
            text="My Laptop",
            link="https://example.com",
        )
        assert "LAPTOP" in svg

    def test_generate_contains_custom_color(self, tmp_path):
        """SVG should use the custom highlight color."""
        filepath = make_image(640, 480, str(tmp_path))
        obj      = make_detected_object(img_w=640, img_h=480)
        gen      = Generator()
        svg      = gen.generate(
            image_path=filepath,
            obj=obj,
            text="Test",
            link="https://example.com",
            color="#27c97a",
        )
        assert "#27c97a" in svg

    def test_generate_default_color(self, tmp_path):
        """SVG should use default blue color when none specified."""
        filepath = make_image(640, 480, str(tmp_path))
        obj      = make_detected_object(img_w=640, img_h=480)
        gen      = Generator()
        svg      = gen.generate(
            image_path=filepath,
            obj=obj,
            text="Test",
            link="https://example.com",
        )
        assert "#3b82f6" in svg

    def test_generate_contains_visit_link(self, tmp_path):
        """SVG should contain the Visit Link button."""
        filepath = make_image(640, 480, str(tmp_path))
        obj      = make_detected_object(img_w=640, img_h=480)
        gen      = Generator()
        svg      = gen.generate(
            image_path=filepath,
            obj=obj,
            text="Test",
            link="https://example.com",
        )
        assert "Visit Link" in svg

    def test_generate_contains_hotspot_group(self, tmp_path):
        """SVG should contain the hotspot-group class."""
        filepath = make_image(640, 480, str(tmp_path))
        obj      = make_detected_object(img_w=640, img_h=480)
        gen      = Generator()
        svg      = gen.generate(
            image_path=filepath,
            obj=obj,
            text="Test",
            link="https://example.com",
        )
        assert "hotspot-group" in svg

    def test_generate_file_not_found(self, tmp_path):
        """Should raise FileNotFoundError for missing image."""
        obj = make_detected_object(img_w=640, img_h=480)
        gen = Generator()
        with pytest.raises(FileNotFoundError):
            gen.generate(
                image_path="/nonexistent/image.jpg",
                obj=obj,
                text="Test",
                link="https://example.com",
            )

    def test_generate_long_text_truncated(self, tmp_path):
        """Long text should be truncated to fit the popup card."""
        filepath  = make_image(640, 480, str(tmp_path))
        obj       = make_detected_object(img_w=640, img_h=480)
        gen       = Generator()
        long_text = "A" * 200
        svg       = gen.generate(
            image_path=filepath,
            obj=obj,
            text=long_text,
            link="https://example.com",
        )
        # SVG should still be generated without errors
        assert "<svg" in svg

    def test_generate_different_labels(self, tmp_path):
        """Should handle different COCO object labels."""
        filepath = make_image(640, 480, str(tmp_path))
        gen      = Generator()
        for label in ["cat", "dog", "person", "laptop", "bottle"]:
            obj = make_detected_object(label=label, img_w=640, img_h=480)
            svg = gen.generate(
                image_path=filepath,
                obj=obj,
                text=f"A {label}",
                link="https://example.com",
            )
            assert label.upper() in svg


# ── Generator.save tests ──────────────────────────────────────────────────────

class TestGeneratorSave:

    def test_save_creates_file(self, tmp_path):
        """save() should create the SVG file on disk."""
        output = os.path.join(str(tmp_path), "output.svg")
        gen    = Generator()
        saved  = gen.save("<svg></svg>", output)
        assert os.path.exists(saved)

    def test_save_returns_absolute_path(self, tmp_path):
        """save() should return an absolute path."""
        output = os.path.join(str(tmp_path), "output.svg")
        gen    = Generator()
        saved  = gen.save("<svg></svg>", output)
        assert os.path.isabs(saved)

    def test_save_adds_svg_extension(self, tmp_path):
        """save() should add .svg extension if missing."""
        output = os.path.join(str(tmp_path), "output")
        gen    = Generator()
        saved  = gen.save("<svg></svg>", output)
        assert saved.endswith(".svg")

    def test_save_file_content(self, tmp_path):
        """Saved file should contain the SVG content."""
        output  = os.path.join(str(tmp_path), "output.svg")
        content = "<svg><rect width='100' height='100'/></svg>"
        gen     = Generator()
        saved   = gen.save(content, output)
        with open(saved, "r", encoding="utf-8") as f:
            assert f.read() == content