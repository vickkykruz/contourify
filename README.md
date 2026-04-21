# contourify
 
> Turn any image into an interactive SVG with AI-powered object detection and clickable hotspots.
 
[![PyPI version](https://badge.fury.io/py/contourify.svg)](https://badge.fury.io/py/contourify)
[![Python](https://img.shields.io/pypi/pyversions/contourify.svg)](https://pypi.org/project/contourify)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-58%20passing-brightgreen.svg)](https://github.com/vickkykruz/contourify)
 
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
 
## Installation
 
```bash
pip install contourify
```
 
---
 
## Quick Start
 
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
from contourify import Contourify
 
ct = Contourify()
 
objects, svg = ct.detect_and_generate(
    image_path="photo.jpg",
    object_id=0,
    text="Sony A7 Camera",
    link="https://shop.example.com/camera",
    color="#27c97a",
)
 
with open("camera_interactive.svg", "w", encoding="utf-8") as f:
    f.write(svg)
```
 
### CLI
 
```bash
# Detect all objects in an image
contourify detect photo.jpg
 
# Output example:
#   Found 3 object(s):
#
#   ID     Label                Confidence
#   ──────  ────────────────────  ────────────
#   0       Chair                91%
#   1       Laptop               85%
#   2       Cup                  63%
#
#   Use the ID above with the generate command:
#   contourify generate photo.jpg --object <ID> --text "..." --link https://...
 
# Generate interactive SVG
contourify generate photo.jpg \
    --object 0 \
    --text "Handcrafted Oak Chair" \
    --link "https://shop.example.com/chair"
 
# With custom color and output path
contourify generate photo.jpg \
    --object 1 \
    --text "Sony A7 Camera" \
    --link "https://shop.example.com/camera" \
    --color "#27c97a" \
    --output camera_hotspot.svg
```
 
---
 
## Image Quality Requirements
 
contourify validates images before processing to ensure accurate detection:
 
| Requirement | Minimum |
|-------------|---------|
| File size | 20 KB |
| Resolution | 300 × 300 px |
| Sharpness | Clear, well-focused |
 
Images that are too small, too low resolution, or blurry will be rejected
with a clear error message explaining what to fix.
 
---
 
## Model Options
 
By default contourify uses `yolov8n-seg` (nano — fastest). For better
accuracy on complex images use a larger model:
 
```python
# More accurate — slower
ct = Contourify(model="yolov8s-seg.pt")  # small
ct = Contourify(model="yolov8m-seg.pt")  # medium
ct = Contourify(model="yolov8l-seg.pt")  # large
```
 
The model is downloaded automatically on first use (~6 MB for nano).
 
---
 
## Telemetry
 
contourify collects **anonymous** usage data to help improve the library.
You are asked once on first run. You can manage this at any time:
 
```bash
contourify --telemetry status   # check current setting
contourify --telemetry off      # disable
contourify --telemetry on       # enable
```
 
Or programmatically:
 
```python
from contourify.telemetry.tracker import disable_telemetry
disable_telemetry()
```
 
**What is collected (with consent):**
 
- Event type (detect, generate, cli_run)
- Platform and Python version
- Approximate country (from ipinfo.io)
**What is never collected:**
 
- Image paths or contents
- SVG output
- Any personally identifying information
Config stored at: `~/.contourify/config.json`
 
---
 
## API Reference
 
### `Contourify(model="yolov8n-seg.pt")`
 
Main class. Initialise once and reuse.
 
### `.detect(image_path, conf=0.25, imgsz=640) → List[DetectedObject]`
 
Detect all objects in an image. Returns list sorted by confidence
descending.
 
### `.generate(image_path, object_id, text, link, color="#3b82f6") → str`
 
Generate interactive SVG for a detected object. Returns SVG string.
 
### `.detect_and_generate(image_path, object_id, text, link, color) → tuple`
 
Convenience method — detect and generate in one call.
Returns `(objects, svg_string)`.
 
### `DetectedObject`
 
| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | int | Zero-based object index |
| `label` | str | COCO class label e.g. `"chair"` |
| `score` | float | Confidence 0–1 |
| `score_pct` | str | Confidence as string e.g. `"91%"` |
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
 