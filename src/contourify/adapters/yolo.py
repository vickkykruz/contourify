"""
    YOLOv8 detection adapter.
 
    Implements BaseDetector using Ultralytics YOLOv8 segmentation.
    This is the default detector used by contourify.
 
    Supported models:
        yolov8n-seg.pt   6.7 MB   Fastest    Good accuracy
        yolov8s-seg.pt   22 MB    Fast       Better accuracy
        yolov8m-seg.pt   52 MB    Medium     Best accuracy
        yolov8l-seg.pt   87 MB    Slow       Excellent accuracy
        yolov8x-seg.pt   136 MB   Slowest    Maximum accuracy
 
    Models are downloaded automatically on first use and cached
    in ~/.contourify/models/
"""
 
from __future__ import annotations
 
import os
from pathlib import Path
from typing import List
 
from contourify.adapters.base import BaseDetector
from contourify.core.detector import BBox, DetectedObject, MODEL_DIR
 
 
# ── Available YOLO models catalogue ──────────────────────────────────────────
YOLO_MODELS = {
    "yolov8n-seg.pt": {
        "size":     "6.7 MB",
        "speed":    "Fastest",
        "accuracy": "Good",
    },
    "yolov8s-seg.pt": {
        "size":     "22 MB",
        "speed":    "Fast",
        "accuracy": "Better",
    },
    "yolov8m-seg.pt": {
        "size":     "52 MB",
        "speed":    "Medium",
        "accuracy": "Best",
    },
    "yolov8l-seg.pt": {
        "size":     "87 MB",
        "speed":    "Slow",
        "accuracy": "Excellent",
    },
    "yolov8x-seg.pt": {
        "size":     "136 MB",
        "speed":    "Slowest",
        "accuracy": "Maximum",
    },
}
 
 
class YOLODetector(BaseDetector):
    """
    YOLOv8 segmentation detector.
 
    Downloads the model automatically on first use to
    ~/.contourify/models/ and caches it there permanently.
 
    Example:
        detector = YOLODetector(model="yolov8s-seg.pt")
        objects  = detector.detect("photo.jpg")
        for obj in objects:
            print(obj.label, obj.score_pct)
    """
 
    def __init__(self, model: str = "yolov8n-seg.pt"):
        """
        Initialise the YOLO detector.
 
        Args:
            model: Model name or full path to a .pt file.
                   Built-in options: yolov8n-seg.pt, yolov8s-seg.pt,
                   yolov8m-seg.pt, yolov8l-seg.pt, yolov8x-seg.pt
                   Custom model: pass absolute path to your .pt file.
                   Defaults to yolov8n-seg.pt (nano - fastest).
        """
        self._model_name = model
        self._model      = None
 
    def _load_model(self) -> None:
        """Lazy load the YOLO model on first use."""
        if self._model is None:
            try:
                from ultralytics import YOLO
 
                model_path = Path(self._model_name)
                if model_path.is_absolute() and model_path.exists():
                    # Custom absolute path — use directly
                    load_path = str(model_path)
                else:
                    # Built-in model — always cache to ~/.contourify/models/
                    cached    = MODEL_DIR / Path(self._model_name).name
                    load_path = str(cached)
 
                self._model = YOLO(load_path)
                self._model.to("cpu")
 
            except ImportError:
                raise ImportError(
                    "ultralytics is required for YOLO detection. "
                    "Install it with: pip install ultralytics"
                )
 
    def detect(
        self,
        image_path: str,
        conf:       float = 0.25,
        imgsz:      int   = 640,
        **kwargs,
    ) -> List[DetectedObject]:
        """
        Detect all objects in an image using YOLOv8 segmentation.
 
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
 
        # orig_shape is (height, width) — numpy convention
        img_h, img_w = results.orig_shape
        objects      = []
 
        if results.masks is not None:
            for i in range(len(results)):
                box             = results.boxes[i]
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf_score      = float(box.conf[0].cpu().numpy())
                cls             = int(box.cls[0].cpu().numpy())
                label           = self._model.names[cls]
 
                bbox = BBox(
                    x1=float(x1 / img_w),
                    y1=float(y1 / img_h),
                    x2=float(x2 / img_w),
                    y2=float(y2 / img_h),
                )
 
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
 
        objects.sort(key=lambda o: o.score, reverse=True)
        return objects
 
    @property
    def name(self) -> str:
        return f"YOLOv8 ({self._model_name})"
 
    @property
    def model_name(self) -> str:
        """Name of the loaded YOLO model."""
        return self._model_name
 
    @property
    def model_cache_dir(self) -> str:
        """Path to the model cache directory."""
        return str(MODEL_DIR)
 