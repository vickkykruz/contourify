"""
    SVG generator.
 
    Builds interactive SVG documents that embed the original
    image as a background layer and overlay the selected object
    contour with a hover popup card containing the user's
    annotation text and a clickable link.
"""
 
from __future__ import annotations
 
import base64
import os
from pathlib import Path
from typing import TYPE_CHECKING
 
if TYPE_CHECKING:
    from contourify.core.detector import DetectedObject
 
 
class Generator:
    """
    Generates self-contained interactive SVG files.
 
    The output SVG:
        - Embeds the original image as base64
        - Draws the object contour as an animated path
        - Shows a styled popup card on hover
        - Contains a clickable Visit Link button
        - Requires no external dependencies
 
    Example:
        generator = Generator()
        svg = generator.generate(
            image_path="photo.jpg",
            obj=detected_object,
            text="Premium Chair",
            link="https://shop.example.com",
            color="#3b82f6",
        )
        with open("output.svg", "w") as f:
            f.write(svg)
 
        # Or wrap in HTML to eliminate white space locally
        html = generator.wrap_html(svg)
        with open("output.html", "w") as f:
            f.write(html)
    """
 
    def generate(
        self,
        image_path: str,
        obj:        "DetectedObject",
        text:       str,
        link:       str,
        color:      str = "#3b82f6",
        label:      str | None = None,
    ) -> str:
        """
        Generate an interactive SVG for a detected object.
 
        Args:
            image_path: Path to the original image file.
            obj:        DetectedObject to annotate.
            text:       Description shown in the hover popup.
            link:       URL opened when Visit Link is clicked.
            color:      Highlight color as hex. Defaults to blue.
            label:      Override the label shown in the popup header.
                        If None the detected object label is used.
                        Useful when YOLO misidentifies an object.
 
        Returns:
            Complete SVG document as a string.
 
        Raises:
            FileNotFoundError: If the image file does not exist.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
 
        w = obj.width
        h = obj.height
 
        # ── Build contour path ────────────────────────────────────────────
        scaled    = [(x * w, y * h) for x, y in obj.contour]
        path_data = (
            "M " + " ".join(f"{x:.1f},{y:.1f}" for x, y in scaled) + " Z"
        )
 
        # ── Embed image as base64 ─────────────────────────────────────────
        suffix   = Path(image_path).suffix.lstrip(".").lower()
        mime     = "jpeg" if suffix in ("jpg", "jpeg") else suffix
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
 
        # ── Label — use override if provided ─────────────────────────────
        display_label = label.upper() if label else obj.label.upper()
 
        # ── Proportional scaling ──────────────────────────────────────────
        scale      = w / 400.0
        popup_w    = w * 0.42
        popup_h    = h * 0.22
        font_label = max(10, 13 * scale)
        font_text  = max(9,  11 * scale)
        font_btn   = max(8,  10 * scale)
        header_h   = popup_h * 0.28
        padding    = popup_w * 0.06
        radius     = max(4, 8 * scale)
        stroke_w   = max(1.5, 2.5 * scale)
        btn_w      = popup_w * 0.52
        btn_h      = popup_h * 0.22
        shadow_off = max(2, 3 * scale)
 
        # ── Popup card positioning ────────────────────────────────────────
        bbox_x1 = obj.bbox.x1 * w
        bbox_y1 = obj.bbox.y1 * h
        bbox_x2 = obj.bbox.x2 * w
        bbox_y2 = obj.bbox.y2 * h
        bbox_cx = (bbox_x1 + bbox_x2) / 2
 
        popup_x = max(4, min(bbox_cx - popup_w / 2, w - popup_w - 4))
 
        # ── Smart popup vertical placement ───────────────────────────────
        # Priority order:
        #   1. Above the object if there is enough room
        #   2. Below the object if there is enough room
        #   3. Clamped inside the image if neither fits cleanly
        margin = 12 * scale
 
        above_y   = bbox_y1 - popup_h - margin
        below_y   = bbox_y2 + margin
        fits_above = above_y >= 4
        fits_below = below_y + popup_h <= h - 4
 
        if fits_above:
            popup_y = above_y
        elif fits_below:
            popup_y = below_y
        else:
            # Neither fits cleanly — centre vertically on the object
            obj_cy  = (bbox_y1 + bbox_y2) / 2
            popup_y = obj_cy - popup_h / 2
 
        # Final clamp — never overflow image bounds
        popup_y = max(4, min(popup_y, h - popup_h - 4))
 
        # ── Derived positions ─────────────────────────────────────────────
        header_bottom = popup_y + header_h
        text_y1       = header_bottom + popup_h * 0.22
        text_y2       = header_bottom + popup_h * 0.42
        btn_x         = popup_x + (popup_w - btn_w) / 2
        btn_y         = popup_y + popup_h - btn_h - popup_h * 0.08
        btn_text_y    = btn_y + btn_h * 0.65
        label_y       = popup_y + header_h * 0.68
        shadow_x      = popup_x + shadow_off
        shadow_y      = popup_y + shadow_off
 
        # ── Text truncation ───────────────────────────────────────────────
        chars_per_line = max(20, int(popup_w / (font_text * 0.6)))
        line1 = text[:chars_per_line]
        line2 = (
            text[chars_per_line: chars_per_line * 2]
            if len(text) > chars_per_line else ""
        )
 
        line2_svg = (
            f'<text x="{popup_x + padding:.1f}" y="{text_y2:.1f}" '
            f'font-family="Arial, sans-serif" font-size="{font_text:.1f}" '
            f'fill="#374151">{line2}</text>'
            if line2 else ""
        )
 
        # ── Build SVG ─────────────────────────────────────────────────────
        svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {w} {h}"
     preserveAspectRatio="xMidYMid meet"
     style="width:100%;height:100%;display:block;">
 
  <style>
    .hotspot-path {{ cursor: pointer; }}
    .hotspot-path:hover {{ fill: rgba(59,130,246,0.35); }}
    .popup {{ visibility: hidden; opacity: 0; transition: opacity 0.18s; pointer-events: none; }}
    .hotspot-group:hover .popup {{ visibility: visible; opacity: 1; pointer-events: all; }}
    .visit-btn rect {{ transition: fill 0.15s; }}
    .visit-btn:hover rect {{ fill: #1d4ed8; }}
  </style>
 
  <!-- Original image embedded as base64 -->
  <image href="data:image/{mime};base64,{img_data}"
         x="0" y="0" width="{w}" height="{h}"
         preserveAspectRatio="xMidYMid meet"/>
 
  <!-- Interactive group: contour + popup card -->
  <g class="hotspot-group">
 
    <!-- Object contour -->
    <path class="hotspot-path"
          d="{path_data}"
          fill="rgba(59,130,246,0.18)"
          stroke="{color}"
          stroke-width="{stroke_w:.1f}"
          stroke-linejoin="round"
          stroke-linecap="round">
      <animate attributeName="stroke-opacity"
               values="0.5;1;0.5" dur="2.5s" repeatCount="indefinite"/>
    </path>
 
    <!-- Popup card -->
    <g class="popup">
 
      <!-- Drop shadow -->
      <rect x="{shadow_x:.1f}" y="{shadow_y:.1f}"
            width="{popup_w:.1f}" height="{popup_h:.1f}"
            rx="{radius:.1f}" ry="{radius:.1f}"
            fill="rgba(0,0,0,0.18)"/>
 
      <!-- Card body -->
      <rect x="{popup_x:.1f}" y="{popup_y:.1f}"
            width="{popup_w:.1f}" height="{popup_h:.1f}"
            rx="{radius:.1f}" ry="{radius:.1f}"
            fill="white" stroke="#e2e8f0" stroke-width="1"/>
 
      <!-- Header band -->
      <rect x="{popup_x:.1f}" y="{popup_y:.1f}"
            width="{popup_w:.1f}" height="{header_h:.1f}"
            rx="{radius:.1f}" ry="{radius:.1f}"
            fill="{color}"/>
      <!-- Square off header bottom corners -->
      <rect x="{popup_x:.1f}" y="{header_bottom - radius:.1f}"
            width="{popup_w:.1f}" height="{radius:.1f}"
            fill="{color}"/>
 
      <!-- Object label — uses override if provided -->
      <text x="{popup_x + popup_w / 2:.1f}" y="{label_y:.1f}"
            text-anchor="middle"
            font-family="Arial, sans-serif"
            font-size="{font_label:.1f}"
            font-weight="bold"
            fill="white">{display_label}</text>
 
      <!-- User description -->
      <text x="{popup_x + padding:.1f}" y="{text_y1:.1f}"
            font-family="Arial, sans-serif"
            font-size="{font_text:.1f}"
            fill="#374151">{line1}</text>
      {line2_svg}
 
      <!-- Visit link button -->
      <a href="{link}" target="_blank">
        <g class="visit-btn">
          <rect x="{btn_x:.1f}" y="{btn_y:.1f}"
                width="{btn_w:.1f}" height="{btn_h:.1f}"
                rx="{radius * 0.5:.1f}" ry="{radius * 0.5:.1f}"
                fill="{color}"/>
          <text x="{btn_x + btn_w / 2:.1f}" y="{btn_text_y:.1f}"
                text-anchor="middle"
                font-family="Arial, sans-serif"
                font-size="{font_btn:.1f}"
                font-weight="bold"
                fill="white">Visit Link \u2192</text>
        </g>
      </a>
 
    </g>
  </g>
 
</svg>"""
 
        return svg
 
    def wrap_html(self, svg: str) -> str:
        """
        Wrap an SVG string in a full-screen HTML page.
 
        This eliminates the white space that browsers add when
        opening a standalone .svg file locally. Use this when
        you want the image to fill the entire browser window.
 
        Args:
            svg: SVG document string from generate().
 
        Returns:
            Complete HTML document as a string.
 
        Example:
            svg  = generator.generate(...)
            html = generator.wrap_html(svg)
            with open("output.html", "w") as f:
                f.write(html)
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>contourify</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: 100%; height: 100%;
      background: #000;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }}
    .svg-container {{
      width: 100vw;
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .svg-container svg {{
      max-width: 100vw;
      max-height: 100vh;
      width: auto;
      height: auto;
    }}
  </style>
</head>
<body>
  <div class="svg-container">
    {svg}
  </div>
</body>
</html>"""
 
    def save(
        self,
        svg:         str,
        output_path: str,
    ) -> str:
        """
        Save SVG string to a file.
 
        Args:
            svg:         SVG document string.
            output_path: Destination file path.
                         Extension is added if missing.
 
        Returns:
            Absolute path to the saved file.
        """
        if not output_path.endswith(".svg"):
            output_path += ".svg"
 
        os.makedirs(
            os.path.dirname(os.path.abspath(output_path)),
            exist_ok=True
        )
 
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg)
 
        return os.path.abspath(output_path)
 
    def save_html(
        self,
        svg:         str,
        output_path: str,
    ) -> str:
        """
        Wrap SVG in HTML and save to a file.
 
        Args:
            svg:         SVG document string from generate().
            output_path: Destination file path.
                         Extension is added if missing.
 
        Returns:
            Absolute path to the saved HTML file.
        """
        if not output_path.endswith(".html"):
            output_path += ".html"
 
        os.makedirs(
            os.path.dirname(os.path.abspath(output_path)),
            exist_ok=True
        )
 
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.wrap_html(svg))
 
        return os.path.abspath(output_path)
 