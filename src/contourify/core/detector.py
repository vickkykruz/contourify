"""
    Object detector.
 
    Wraps YOLOv8 segmentation to detect objects in images
    and return normalised contour points and bounding boxes.
"""
 
from __future__ import annotations
 
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
 
 
# ── Model cache directory ─────────────────────────────────────────────────────
# Models are always saved here regardless of working directory
MODEL_DIR = Path.home() / ".contourify" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
 
 
@dataclass
class BBox:
    """Normalised bounding box (0-1 range)."""
    x1: float
    y1: float
    x2: float
    y2: float
 
    @property
    def width(self) -> float:
        return self.x2 - self.x1
 
    @property
    def height(self) -> float:
        return self.y2 - self.y1
 
    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2
 
    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2
 
 
@dataclass
class DetectedObject:
    """
    A single detected object in an image.
 
    Attributes:
        id:      Zero-based index of this object.
        label:   COCO class label e.g. 'cat', 'chair'.
        score:   Confidence score between 0 and 1.
        bbox:    Normalised bounding box.
        contour: List of [x, y] normalised contour points.
        width:   Natural image width in pixels.
        height:  Natural image height in pixels.
    """
    id:      int
    label:   str
    score:   float
    bbox:    BBox
    contour: List[List[float]] = field(default_factory=list)
    width:   int = 0
    height:  int = 0
 
    @property
    def score_pct(self) -> str:
        """Confidence as a percentage string e.g. '91%'."""
        return f"{self.score:.0%}"
 
    def __repr__(self) -> str:
        return (
            f"DetectedObject(id={self.id}, label='{self.label}', "
            f"score={self.score_pct})"
        )
 
 
class Detector:
    """
    YOLOv8 segmentation wrapper.
 
    Downloads the model automatically on first use to
    ~/.contourify/models/ and caches it there permanently.
    Subsequent calls use the cached model.
 
    Example:
        detector = Detector()
        objects  = detector.detect("photo.jpg")
        for obj in objects:
            print(obj.label, obj.score_pct)
    """
 
    def __init__(self, model: str = "yolov8n-seg.pt"):
        """
        Initialise the detector.
 
        Args:
            model: YOLOv8 segmentation model name or full path.
                   Options: yolov8n-seg.pt, yolov8s-seg.pt,
                            yolov8m-seg.pt, yolov8l-seg.pt
                   Larger models are slower but more accurate.
                   Defaults to yolov8n-seg (nano - fastest).
        """
        self._model_name = model
        self._model      = None
 
    def _load_model(self):
        """Lazy load the YOLO model on first use."""
        if self._model is None:
            try:
                from ultralytics import YOLO
 
                # If it's a full absolute path use it directly
                model_path = Path(self._model_name)
                if model_path.is_absolute() and model_path.exists():
                    load_path = str(model_path)
                else:
                    # Always cache to ~/.contourify/models/
                    cached = MODEL_DIR / Path(self._model_name).name
                    load_path = str(cached)
 
                self._model = YOLO(load_path)
                self._model.to("cpu")
 
            except ImportError:
                raise ImportError(
                    "ultralytics is required for object detection. "
                    "Install it with: pip install ultralytics"
                )
 
    def detect(
        self,
        image_path: str,
        conf:       float = 0.25,
        imgsz:      int   = 640,
    ) -> List[DetectedObject]:
        """
        Detect all objects in an image.
 
        Args:
            image_path: Path to the image file.
            conf:       Minimum confidence threshold (0-1).
                        Lower values detect more objects but
                        may include false positives.
                        Defaults to 0.25.
            imgsz:      Input image size for YOLO inference.
                        Defaults to 640.
 
        Returns:
            List of DetectedObject instances sorted by
            confidence score descending.
 
        Raises:
            FileNotFoundError: If the image does not exist.
            RuntimeError:      If YOLO inference fails.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
 
        self._load_model()
 
        try:
            results = self._model(
                source=image_path,
                device="cpu",
                imgsz=imgsz,
                conf=conf,
                verbose=False,
                retina_masks=True,
            )[0]
        except Exception as e:
            raise RuntimeError(f"YOLO inference failed: {e}")
 
        # ── Parse results ─────────────────────────────────────────────────
        # orig_shape is (height, width) — numpy convention
        img_h, img_w = results.orig_shape
        objects      = []
 
        if results.masks is not None:
            for i in range(len(results)):
                box   = results.boxes[i]
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf_score      = float(box.conf[0].cpu().numpy())
                cls             = int(box.cls[0].cpu().numpy())
                label           = self._model.names[cls]
 
                # Correct: normalize x by img_w, y by img_h
                bbox = BBox(
                    x1=float(x1 / img_w),
                    y1=float(y1 / img_h),
                    x2=float(x2 / img_w),
                    y2=float(y2 / img_h),
                )
 
                # Normalize contour points
                mask_xy            = results.masks.xy[i]
                contour_normalized = [
                    [float(pt[0] / img_w), float(pt[1] / img_h)]
                    for pt in mask_xy
                ]
 
                objects.append(DetectedObject(
                    id=i,
                    label=label,
                    score=conf_score,
                    bbox=bbox,
                    contour=contour_normalized,
                    width=img_w,
                    height=img_h,
                ))
 
        # Sort by confidence descending
        objects.sort(key=lambda o: o.score, reverse=True)
        return objects
 
    @property
    def model_name(self) -> str:
        """Name of the loaded YOLO model."""
        return self._model_name
 
    @property
    def model_cache_dir(self) -> str:
        """Path to the model cache directory."""
        return str(MODEL_DIR)
 