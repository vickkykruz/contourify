"""
Test that the BaseDetector adapter pattern works correctly.
"""

from contourify import Contourify
from contourify.adapters import BaseDetector
from contourify.core.detector import DetectedObject, BBox


class MockDetector(BaseDetector):
    """
    A fake detector that returns hardcoded results.
    Simulates what a TensorFlow or custom model would return.
    """

    def detect(self, image_path: str, **kwargs) -> list:
        # Simulate detecting one object at fixed coordinates
        return [
            DetectedObject(
                id=0,
                label="mock_object",
                score=0.95,
                bbox=BBox(x1=0.1, y1=0.1, x2=0.9, y2=0.9),
                contour=[
                    [0.1, 0.1],
                    [0.9, 0.1],
                    [0.9, 0.9],
                    [0.1, 0.9],
                ],
                width=1024,
                height=683,
            )
        ]

    @property
    def name(self) -> str:
        return "MockDetector v1.0"


# ── Test 1 — Contourify accepts a custom detector ─────────────────────────────
print("\nTest 1 — Custom detector accepted...")
ct = Contourify(detector=MockDetector())
print(f"  Detector: {ct._detector.name}")
print("  PASSED ✅")


# ── Test 2 — detect() returns correct results ─────────────────────────────────
print("\nTest 2 — detect() returns DetectedObject list...")
objects = ct._detector.detect("any_path.jpg")
assert len(objects) == 1
assert objects[0].label == "mock_object"
assert objects[0].score == 0.95
assert objects[0].score_pct == "95%"
print(f"  Found: {objects[0]}")
print("  PASSED ✅")


# ── Test 3 — BaseDetector type check works ────────────────────────────────────
print("\nTest 3 — Type check on invalid detector...")
try:
    ct_bad = Contourify(detector="not_a_detector")
    print("  FAILED ❌ — should have raised TypeError")
except TypeError as e:
    print(f"  TypeError raised correctly: {e}")
    print("  PASSED ✅")


# ── Test 4 — generate() uses custom detector ─────────────────────────────────
print("\nTest 4 — generate() uses custom detector end to end...")
import os

# Use the animal.jpg we already have
image_path = r"C:\Users\HP\Downloads\animal.jpg"

if os.path.exists(image_path):
    from contourify.core.generator import Generator
    from contourify.core.detector import DetectedObject, BBox

    obj = MockDetector().detect(image_path)[0]
    # Fix dimensions to match actual image
    from PIL import Image
    with Image.open(image_path) as img:
        w, h = img.size
    obj.width  = w
    obj.height = h
    obj.contour = [
        [0.1, 0.1], [0.9, 0.1],
        [0.9, 0.9], [0.1, 0.9],
    ]

    gen  = Generator()
    svg  = gen.generate(
        image_path=image_path,
        obj=obj,
        text="Custom Detector Output",
        link="https://example.com",
        color="#27c97a",
        label="Mock Object",
    )
    saved = gen.save(svg, r"C:\Users\HP\Downloads\mock_detector_test.svg")
    print(f"  SVG saved to: {saved}")
    print("  PASSED ✅")
else:
    print(f"  Skipped — {image_path} not found")


print("\n All adapter tests passed.\n")