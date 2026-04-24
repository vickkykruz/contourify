<p align="center">
  <img src="https://i.ibb.co/pBGtZb8b/contourify-logo.png" alt="contourify" width="240"/>
</p>
<p align="center">
  <strong>Turn any image into an interactive SVG with AI-powered object detection and clickable hotspots.</strong>
</p>
<p align="center">
  <a href="https://badge.fury.io/py/contourify"><img src="https://badge.fury.io/py/contourify.svg" alt="PyPI version"/></a>
  <a href="https://pypi.org/project/contourify"><img src="https://img.shields.io/pypi/pyversions/contourify.svg" alt="Python"/></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License"/></a>
  <a href="https://github.com/vickkykruz/contourify"><img src="https://img.shields.io/badge/tests-58%20passing-brightgreen.svg" alt="Tests"/></a>
</p>
---
 
## What is contourify?
 
**contourify** is a Python library that combines AI object detection with
interactive SVG generation. Upload any image, detect the objects inside it,
pick one, attach a description and a link — and get back a single
self-contained `.svg` file that works in any browser with no external
dependencies.
 
```
photo.jpg  →  contourify  →  photo_contourify.svg
```
 
The output SVG:
 
- Embeds the original image
- Draws an animated contour around the selected object
- Shows a styled popup card on hover with your description
- Contains a clickable **Visit Link** button
- Works anywhere SVG is supported — browsers, email, Discord, LinkedIn
---
 
## Demo
 
### Input → Output
 
> **Step 1** — Run `contourify detect` on your image
 
<!-- DEMO: Replace the block below with a screenshot of the terminal
     showing the detect command output.
     Suggested filename: docs/demo_detect.png
     Example:
     ![Detect output](docs/demo_detect.png)
-->
 
```
  Detecting objects in: product.jpg
  Model: yolov8n-seg.pt
 
  Found 3 object(s):
 
  ID     Label                Confidence
  ──────  ────────────────────  ────────────
  0       Chair                91%
  1       Laptop               85%
  2       Cup                  63%
```
 
---
 
> **Step 2** — Run `contourify generate` to produce the interactive file
 
<!-- DEMO: Replace this comment with a side-by-side comparison image
     showing the original photo on the left and the SVG output on the right.
     Suggested filename: docs/demo_generate.png
     Example:
     ![Original vs SVG output](docs/demo_generate.png)
-->
 
---
 
> **Step 3** — Open the file in any browser and hover over the object
 
<!-- DEMO: Replace this comment with a screenshot of the SVG open in a browser
     with the popup card fully visible on hover.
     Suggested filename: docs/demo_hover.png
     Example:
     ![Hover popup card](docs/demo_hover.png)
-->
 
---
 
### Full pipeline
 
```
┌─────────────┐    contourify detect     ┌──────────────────────┐
│  photo.jpg  │ ────────────────────►   │  0: Chair  91%       │
│             │                          │  1: Laptop 85%       │
└─────────────┘                          └──────────────────────┘
                                                    │
                                  contourify generate --object 0
                                                    │
                                                    ▼
                                      ┌─────────────────────────┐
                                      │  photo_contourify.svg   │
                                      │  ┌───────────────────┐  │
                                      │  │ [animated outline] │  │
                                      │  │  ┌─────────────┐  │  │
                                      │  │  │   CHAIR     │  │  │
                                      │  │  │  Oak Chair  │  │  │
                                      │  │  │ Visit Link →│  │  │
                                      │  │  └─────────────┘  │  │
                                      │  └───────────────────┘  │
                                      └─────────────────────────┘
```
 
---
 
## Installation
 
```bash
pip install contourify
```
 
---
 
## Quick Start
 
### CLI
 
```bash
# Show the full getting started guide
contourify help
 
# Step 1 — detect objects in your image
contourify detect photo.jpg
 
# Step 2 — generate interactive SVG
contourify generate photo.jpg \
    --object 0 \
    --text "Handcrafted Oak Chair" \
    --link "https://shop.example.com/chair"
 
# HTML output — no white space when opened locally
contourify generate photo.jpg \
    --object 0 \
    --text "Handcrafted Oak Chair" \
    --link "https://shop.example.com/chair" \
    --format html
 
# Override a misdetected label
contourify generate photo.jpg \
    --object 0 \
    --text "Beautiful Fallow Deer" \
    --link "https://example.com" \
    --label "Deer"
 
# Custom color and output path
contourify generate photo.jpg \
    --object 1 \
    --text "Sony A7 Camera" \
    --link "https://shop.example.com/camera" \
    --color "#27c97a" \
    --output camera_hotspot.svg
```
 
### Python API
 
```python
from contourify import Contourify
 
ct = Contourify()
 
# Step 1 — detect objects
objects = ct.detect("photo.jpg")
for obj in objects:
    print(f"{obj.id}: {obj.label} ({obj.score_pct})")
 
# Step 2 — generate interactive SVG
svg = ct.generate(
    image_path="photo.jpg",
    object_id=0,
    text="Handcrafted Oak Chair — Free shipping worldwide",
    link="https://shop.example.com/chair",
    color="#3b82f6",
)
 
# Step 3 — save to file
with open("chair_interactive.svg", "w", encoding="utf-8") as f:
    f.write(svg)
```
 
### One-call API
 
```python
objects, svg = ct.detect_and_generate(
    image_path="photo.jpg",
    object_id=0,
    text="Sony A7 Camera",
    link="https://shop.example.com/camera",
    color="#27c97a",
)
```
 
### HTML output
 
```python
html = ct.generate(
    image_path="photo.jpg",
    object_id=0,
    text="My Product",
    link="https://example.com",
    fmt="html",   # full-screen, no white space when opened locally
)
```
 
### Label override
 
```python
svg = ct.generate(
    image_path="photo.jpg",
    object_id=0,
    text="Beautiful Fallow Deer",
    link="https://example.com",
    label="Deer",   # overrides whatever the model detected
)
```
 
---
 
## Model Management
 
### List available models
 
```bash
contourify models list
```
 
```
  Available models:
 
  Name                   Size       Speed        Accuracy
  ──────────────────────  ──────────  ────────────  ────────────
  yolov8n-seg.pt         6.7 MB     Fastest      Good         <- default
  yolov8s-seg.pt         22 MB      Fast         Better
  yolov8m-seg.pt         52 MB      Medium       Best
  yolov8l-seg.pt         87 MB      Slow         Excellent
  yolov8x-seg.pt         136 MB     Slowest      Maximum
```
 
### Set default model
 
```bash
contourify models set yolov8s      # set small as default
contourify models set yolov8m      # set medium as default
contourify models set yolov8n      # reset to nano (fastest)
```
 
### Pre-download models
 
```bash
contourify models download yolov8s     # download one model
contourify models download all         # download all models
```
 
### Use a model in Python
 
```python
ct = Contourify(model="yolov8s-seg.pt")     # small — better accuracy
ct = Contourify(model="yolov8m-seg.pt")     # medium — best accuracy
ct = Contourify(model="/path/to/custom.pt") # custom model path
```
 
Models are cached in `~/.contourify/models/` and never redownloaded.
 
---
 
## Custom Detectors
 
contourify supports any detection backend via the `BaseDetector` adapter pattern.
Plug in TensorFlow, custom trained models, or any other framework.
 
```python
from contourify import Contourify
from contourify.adapters import BaseDetector
from contourify.core.detector import DetectedObject, BBox
 
class MyCustomDetector(BaseDetector):
 
    def detect(self, image_path: str, **kwargs) -> list:
        # Run your model here and return DetectedObject instances
        return [
            DetectedObject(
                id=0,
                label="my_object",
                score=0.95,
                bbox=BBox(x1=0.1, y1=0.1, x2=0.9, y2=0.9),
                contour=[
                    [0.1, 0.1], [0.9, 0.1],
                    [0.9, 0.9], [0.1, 0.9],
                ],
                width=640,
                height=480,
            )
        ]
 
    @property
    def name(self) -> str:
        return "MyCustomDetector v1.0"
 
 
# Use with Contourify — everything else works identically
ct = Contourify(detector=MyCustomDetector())
objects = ct.detect("photo.jpg")
svg = ct.generate(
    image_path="photo.jpg",
    object_id=0,
    text="My detected object",
    link="https://example.com",
)
```
 
### DetectedObject contract
 
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | int | ✅ | Zero-based object index |
| `label` | str | ✅ | Object class name |
| `score` | float | ✅ | Confidence 0–1 |
| `bbox` | BBox | ✅ | Normalised bounding box (0–1 range) |
| `contour` | list | ✅ | Normalised `[[x, y], ...]` contour points |
| `width` | int | ✅ | Natural image width in pixels |
| `height` | int | ✅ | Natural image height in pixels |
 
---
 
## Image Quality Requirements
 
| Requirement | Minimum |
|-------------|---------|
| File size | 20 KB |
| Resolution | 300 × 300 px |
| Sharpness | Clear, well-focused |
 
---
 
## Telemetry
 
contourify collects **anonymous** usage data to help improve the library.
You are asked once on first run. You can manage this at any time:
 
```bash
contourify --telemetry status
contourify --telemetry off
contourify --telemetry on
```
 
**Collected (with consent):** event type, platform, Python version, approximate country.
**Never collected:** image paths, SVG output, personal data.
 
Config stored at: `~/.contourify/config.json`
 
---
 
## API Reference
 
### `Contourify(model=None, detector=None)`
 
- `model` — YOLOv8 model name or path. Defaults to `yolov8n-seg.pt`.
- `detector` — Custom `BaseDetector` instance. Overrides `model` if provided.
### `.detect(image_path) → List[DetectedObject]`
 
Detect all objects. Returns list sorted by confidence descending.
 
### `.generate(image_path, object_id, text, link, color, label, fmt) → str`
 
Generate interactive SVG or HTML. `fmt` is `"svg"` (default) or `"html"`.
 
### `.detect_and_generate(...) → tuple`
 
One-call convenience. Returns `(objects, output_string)`.
 
### `DetectedObject`
 
| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | int | Zero-based object index |
| `label` | str | COCO class label e.g. `"chair"` |
| `score` | float | Confidence 0–1 |
| `score_pct` | str | e.g. `"91%"` |
| `bbox` | BBox | Normalised bounding box |
| `contour` | list | Normalised contour points |
| `width` | int | Image width in pixels |
| `height` | int | Image height in pixels |
 
---
 
## Requirements
 
- Python 3.9+
- ultralytics >= 8.0.0
- pillow >= 9.0.0
- opencv-python-headless >= 4.5.0
- click >= 8.0.0
- requests >= 2.28.0
---
 
## License
 
MIT — see [LICENSE](LICENSE) for details.
 
---
 
## Author
 
**Victor Chukwuemeka**
 
- GitHub: [@vickkykruz](https://github.com/vickkykruz)
- Portfolio: [vickkykruzprogramming.dev](https://vickkykruzprogramming.dev)
---
 
*contourify powers the
[Photo Contour](https://github.com/vickkykruz/Photo-Contour)
web studio.*
 
