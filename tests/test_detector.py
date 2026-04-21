"""
    Tests for object detector.

    Note: These tests do not run actual YOLO inference
    (which requires downloading the model and is slow).
    Instead they test the Detector class structure, the
    DetectedObject dataclass, and the BBox dataclass.

    Full integration tests with real YOLO inference are
    handled separately in tests/test_integration.py.
"""

import pytest

from contourify.core.detector import BBox, DetectedObject, Detector


# ── BBox tests ────────────────────────────────────────────────────────────────

class TestBBox:

    def test_basic_creation(self):
        """BBox should be created with x1, y1, x2, y2."""
        bbox = BBox(x1=0.1, y1=0.2, x2=0.8, y2=0.9)
        assert bbox.x1 == 0.1
        assert bbox.y1 == 0.2
        assert bbox.x2 == 0.8
        assert bbox.y2 == 0.9

    def test_width_property(self):
        """width should be x2 - x1."""
        bbox = BBox(x1=0.1, y1=0.0, x2=0.6, y2=1.0)
        assert pytest.approx(bbox.width) == 0.5

    def test_height_property(self):
        """height should be y2 - y1."""
        bbox = BBox(x1=0.0, y1=0.2, x2=1.0, y2=0.7)
        assert pytest.approx(bbox.height) == 0.5

    def test_center_x_property(self):
        """center_x should be midpoint of x1 and x2."""
        bbox = BBox(x1=0.2, y1=0.0, x2=0.8, y2=1.0)
        assert pytest.approx(bbox.center_x) == 0.5

    def test_center_y_property(self):
        """center_y should be midpoint of y1 and y2."""
        bbox = BBox(x1=0.0, y1=0.2, x2=1.0, y2=0.8)
        assert pytest.approx(bbox.center_y) == 0.5

    def test_normalized_values(self):
        """BBox values should be between 0 and 1."""
        bbox = BBox(x1=0.0, y1=0.0, x2=1.0, y2=1.0)
        assert 0.0 <= bbox.x1 <= 1.0
        assert 0.0 <= bbox.y1 <= 1.0
        assert 0.0 <= bbox.x2 <= 1.0
        assert 0.0 <= bbox.y2 <= 1.0

    def test_square_bbox(self):
        """Square bounding box should have equal width and height."""
        bbox = BBox(x1=0.1, y1=0.1, x2=0.9, y2=0.9)
        assert pytest.approx(bbox.width) == pytest.approx(bbox.height)


# ── DetectedObject tests ──────────────────────────────────────────────────────

class TestDetectedObject:

    def make_obj(self, **kwargs) -> DetectedObject:
        defaults = dict(
            id=0,
            label="chair",
            score=0.91,
            bbox=BBox(x1=0.2, y1=0.2, x2=0.8, y2=0.8),
            contour=[[0.2, 0.2], [0.8, 0.2], [0.8, 0.8], [0.2, 0.8]],
            width=640,
            height=480,
        )
        defaults.update(kwargs)
        return DetectedObject(**defaults)

    def test_basic_creation(self):
        """DetectedObject should be created with all fields."""
        obj = self.make_obj()
        assert obj.id    == 0
        assert obj.label == "chair"
        assert obj.score == 0.91
        assert obj.width == 640
        assert obj.height == 480

    def test_score_pct_property(self):
        """score_pct should format score as percentage string."""
        obj = self.make_obj(score=0.91)
        assert obj.score_pct == "91%"

    def test_score_pct_rounds(self):
        """score_pct should round to nearest percent."""
        obj = self.make_obj(score=0.855)
        assert obj.score_pct == "86%"

    def test_repr(self):
        """__repr__ should include id, label and score."""
        obj  = self.make_obj(id=2, label="laptop", score=0.78)
        text = repr(obj)
        assert "2"      in text
        assert "laptop" in text
        assert "78%"    in text

    def test_default_contour(self):
        """DetectedObject should default to empty contour list."""
        obj = DetectedObject(
            id=0,
            label="cat",
            score=0.9,
            bbox=BBox(x1=0.1, y1=0.1, x2=0.9, y2=0.9),
        )
        assert obj.contour == []

    def test_contour_points_normalized(self):
        """Contour points should be in 0-1 range."""
        obj = self.make_obj()
        for point in obj.contour:
            assert len(point) == 2
            assert 0.0 <= point[0] <= 1.0
            assert 0.0 <= point[1] <= 1.0

    def test_multiple_objects_different_ids(self):
        """Multiple objects should have different IDs."""
        obj0 = self.make_obj(id=0, label="chair")
        obj1 = self.make_obj(id=1, label="laptop")
        obj2 = self.make_obj(id=2, label="cat")
        assert obj0.id != obj1.id
        assert obj1.id != obj2.id
        assert obj0.id != obj2.id

    def test_high_confidence_score(self):
        """Score of 1.0 should format as 100%."""
        obj = self.make_obj(score=1.0)
        assert obj.score_pct == "100%"

    def test_low_confidence_score(self):
        """Score of 0.01 should format as 1%."""
        obj = self.make_obj(score=0.01)
        assert obj.score_pct == "1%"

    def test_bbox_accessible(self):
        """BBox should be accessible and have correct values."""
        bbox = BBox(x1=0.1, y1=0.2, x2=0.7, y2=0.8)
        obj  = self.make_obj(bbox=bbox)
        assert obj.bbox.x1 == 0.1
        assert obj.bbox.y1 == 0.2
        assert obj.bbox.x2 == 0.7
        assert obj.bbox.y2 == 0.8


# ── Detector class tests ──────────────────────────────────────────────────────

class TestDetector:

    def test_default_model_name(self):
        """Default model should be yolov8n-seg.pt."""
        detector = Detector()
        assert detector.model_name == "yolov8n-seg.pt"

    def test_custom_model_name(self):
        """Custom model name should be stored correctly."""
        detector = Detector(model="yolov8s-seg.pt")
        assert detector.model_name == "yolov8s-seg.pt"

    def test_model_not_loaded_on_init(self):
        """Model should not be loaded until detect() is called."""
        detector = Detector()
        assert detector._model is None

    def test_detect_file_not_found(self):
        """detect() should raise FileNotFoundError for missing file."""
        detector = Detector()
        with pytest.raises(FileNotFoundError):
            detector.detect("/nonexistent/image.jpg")

    def test_model_name_property(self):
        """model_name property should return the model name."""
        detector = Detector(model="yolov8m-seg.pt")
        assert detector.model_name == "yolov8m-seg.pt"

    def test_detector_accepts_conf_parameter(self, tmp_path):
        """
        detect() should accept conf parameter without error.
        We test this by checking FileNotFoundError is raised
        (not TypeError from wrong parameters).
        """
        detector = Detector()
        with pytest.raises(FileNotFoundError):
            detector.detect("/nonexistent/image.jpg", conf=0.15)

    def test_detector_accepts_imgsz_parameter(self, tmp_path):
        """
        detect() should accept imgsz parameter without error.
        """
        detector = Detector()
        with pytest.raises(FileNotFoundError):
            detector.detect("/nonexistent/image.jpg", imgsz=320)