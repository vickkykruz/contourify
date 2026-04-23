"""
    contourify CLI - Command line interface.
 
    Usage:
        contourify detect IMAGE
        contourify generate IMAGE --object 0 --text "My Product" --link https://example.com
        contourify generate IMAGE --object 0 --text "My Product" --link https://example.com --format html
        contourify generate IMAGE --object 0 --text "My Product" --link https://example.com --label "Deer"
        contourify generate IMAGE --object 0 --text "My Product" --link https://example.com --output result.svg
        contourify generate IMAGE --object 0 --text "My Product" --link https://example.com --color "#27c97a"
        contourify info
        contourify --telemetry on|off|status
        contourify --version
"""
 
from __future__ import annotations
 
import os
import sys
 
import click
 
from contourify import Contourify, __version__
from contourify.telemetry.tracker import (
    prompt_first_run,
    handle_telemetry_flag,
    track_detect,
    track_generate,
    track_cli_run,
)
 
 
# ── CLI group ─────────────────────────────────────────────────────────────────
 
@click.group()
@click.version_option(version=__version__, prog_name="contourify")
@click.option(
    "--telemetry",
    default=None,
    metavar="on|off|status",
    help="Manage anonymous usage telemetry.",
)
@click.pass_context
def cli(ctx: click.Context, telemetry: str | None) -> None:
    """
    contourify - Turn any image into an interactive SVG
    with AI-powered object detection and clickable hotspots.
 
    \b
    Step 1 — detect objects in your image:
        contourify detect photo.jpg
 
    \b
    Step 2 — generate interactive SVG:
        contourify generate photo.jpg --object 0 --text "My Chair" --link https://example.com
 
    \b
    Step 2 (HTML — no white space when opened locally):
        contourify generate photo.jpg --object 0 --text "My Chair" --link https://example.com --format html
 
    \b
    Override a misdetected label:
        contourify generate photo.jpg --object 0 --text "Fallow Deer" --link https://example.com --label "Deer"
 
    \b
    Telemetry:
        contourify --telemetry status
        contourify --telemetry off
    """
    if telemetry is not None:
        handle_telemetry_flag(telemetry)
        ctx.exit()
 
    prompt_first_run()
 
 
# ── detect command ────────────────────────────────────────────────────────────
 
@cli.command()
@click.argument("image", type=click.Path(exists=True))
@click.option(
    "--model", "-m",
    default="yolov8n-seg.pt",
    show_default=True,
    help="YOLOv8 segmentation model to use.",
)
@click.option(
    "--conf", "-c",
    default=0.25,
    show_default=True,
    type=float,
    help="Minimum confidence threshold (0-1).",
)
def detect(image: str, model: str, conf: float) -> None:
    """
    Detect all objects in an IMAGE.
 
    \b
    Examples:
        contourify detect photo.jpg
        contourify detect photo.jpg --conf 0.15
        contourify detect photo.jpg --model yolov8s-seg.pt
 
    \b
    Output:
        Lists all detected objects with their ID,
        label and confidence score.
        Use the ID with the generate command.
 
    \b
    Supported objects (80 COCO classes):
        People, animals (cat, dog, horse, cow, sheep, bird,
        elephant, bear, zebra, giraffe), vehicles, furniture,
        electronics, food, sports equipment and more.
    """
    track_cli_run("detect")
 
    click.echo(f"\n  Detecting objects in: {os.path.basename(image)}\n")
 
    try:
        ct      = Contourify(model=model)
        objects = ct.detect(image)
    except ValueError as e:
        click.echo(f"  Image rejected: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"  Detection failed: {e}", err=True)
        sys.exit(1)
 
    if not objects:
        click.echo("  No objects detected.")
        click.echo()
        click.echo("  Tips:")
        click.echo("    - Use a clearer, well-focused image")
        click.echo("    - Lower the confidence: --conf 0.15")
        click.echo("    - Try a larger model: --model yolov8s-seg.pt")
        click.echo()
        click.echo(
            "  Note: contourify detects 80 common object types including"
        )
        click.echo(
            "  people, animals, furniture, vehicles, food and electronics."
        )
        click.echo(
            "  Uncommon subjects like wildlife may not be recognised."
        )
        return
 
    # ── Print results table ───────────────────────────────────────────────
    click.echo(f"  Found {len(objects)} object(s):\n")
    click.echo(f"  {'ID':<6} {'Label':<20} {'Confidence':<12}")
    click.echo(f"  {'─' * 6} {'─' * 20} {'─' * 12}")
 
    for obj in objects:
        click.echo(
            f"  {obj.id:<6} {obj.label.capitalize():<20} {obj.score_pct:<12}"
        )
 
    # ── Low confidence warning ────────────────────────────────────────────
    low_conf = [o for o in objects if o.score < 0.4]
    if low_conf:
        click.echo()
        click.echo("  Warning: Some detections have low confidence.")
        click.echo(
            "  The label may be incorrect if the object is not in"
        )
        click.echo(
            "  the 80 supported COCO classes (e.g. deer, fox, wolf)."
        )
        click.echo("  Use --label to override the displayed label:")
        click.echo(
            f"  contourify generate {os.path.basename(image)} "
            "--object <ID> --text \"...\" --link ... --label \"YourLabel\""
        )
 
    click.echo()
    click.echo("  Next step — generate your interactive SVG:")
    click.echo(
        f"  contourify generate {os.path.basename(image)} "
        "--object <ID> --text \"...\" --link https://..."
    )
    click.echo()
 
    track_detect(len(objects))
 
 
# ── generate command ──────────────────────────────────────────────────────────
 
@cli.command()
@click.argument("image", type=click.Path(exists=True))
@click.option(
    "--object", "-o",
    "object_id",
    required=True,
    type=int,
    help="ID of the detected object to annotate (from detect command).",
)
@click.option(
    "--text", "-t",
    required=True,
    help="Description shown in the hover popup card.",
)
@click.option(
    "--link", "-l",
    required=True,
    help="URL opened when the Visit Link button is clicked.",
)
@click.option(
    "--color",
    default="#3b82f6",
    show_default=True,
    help="Highlight color as a hex string.",
)
@click.option(
    "--label",
    default=None,
    help=(
        "Override the label shown in the popup card header. "
        "Use this when YOLO misidentifies an object. "
        "Example: --label \"Deer\" when YOLO says Sheep."
    ),
)
@click.option(
    "--format", "fmt",
    default="svg",
    show_default=True,
    type=click.Choice(["svg", "html"], case_sensitive=False),
    help=(
        "Output format. "
        "'svg' (default) — standard SVG file. "
        "'html' — full-screen HTML wrapper, eliminates white "
        "space when opening locally in a browser."
    ),
)
@click.option(
    "--output",
    default=None,
    help=(
        "Output file path. "
        "Defaults to <image_name>_contourify.svg (or .html) "
        "in the same folder as the image."
    ),
)
@click.option(
    "--model", "-m",
    default="yolov8n-seg.pt",
    show_default=True,
    help="YOLOv8 segmentation model to use.",
)
def generate(
    image:     str,
    object_id: int,
    text:      str,
    link:      str,
    color:     str,
    label:     str | None,
    fmt:       str,
    output:    str | None,
    model:     str,
) -> None:
    """
    Generate an interactive SVG (or HTML) for a detected object.
 
    \b
    Basic example:
        contourify generate photo.jpg \\
            --object 0 \\
            --text "Handcrafted Oak Chair" \\
            --link https://shop.example.com/chair
 
    \b
    HTML output (no white space when opened locally):
        contourify generate photo.jpg \\
            --object 0 \\
            --text "Handcrafted Oak Chair" \\
            --link https://shop.example.com/chair \\
            --format html
 
    \b
    Override a misdetected label:
        contourify generate photo.jpg \\
            --object 0 \\
            --text "Beautiful Fallow Deer" \\
            --link https://wildlife.example.com \\
            --label "Deer"
 
    \b
    Custom color and output path:
        contourify generate photo.jpg \\
            --object 1 \\
            --text "Sony A7 Camera" \\
            --link https://shop.example.com/camera \\
            --color "#27c97a" \\
            --output camera_hotspot.svg
    """
    track_cli_run("generate")
 
    # ── Default output path ───────────────────────────────────────────────
    ext = ".html" if fmt == "html" else ".svg"
    if output is None:
        base   = os.path.splitext(os.path.basename(image))[0]
        folder = os.path.dirname(os.path.abspath(image))
        output = os.path.join(folder, f"{base}_contourify{ext}")
 
    click.echo(f"\n  Processing: {os.path.basename(image)}")
    click.echo(f"  Object ID:  {object_id}")
    click.echo(f"  Text:       {text}")
    click.echo(f"  Link:       {link}")
    click.echo(f"  Color:      {color}")
    click.echo(f"  Format:     {fmt.upper()}")
    if label:
        click.echo(f"  Label:      {label} (override)")
    click.echo()
 
    try:
        ct     = Contourify(model=model)
        result = ct.generate(
            image_path=image,
            object_id=object_id,
            text=text,
            link=link,
            color=color,
            label=label,
            fmt=fmt,
        )
    except FileNotFoundError as e:
        click.echo(f"  {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"  {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"  Generation failed: {e}", err=True)
        sys.exit(1)
 
    # ── Save output ───────────────────────────────────────────────────────
    try:
        from contourify.core.generator import Generator
        gen   = Generator()
        saved = (
            gen.save_html(result, output)
            if fmt == "html"
            else gen.save(result, output)
        )
        click.echo(f"  Saved to: {saved}")
        click.echo()
        click.echo("  Open the file in any browser to see the")
        click.echo("  interactive hotspot.")
        click.echo()
    except Exception as e:
        click.echo(f"  Could not save output: {e}", err=True)
        sys.exit(1)
 
    track_generate(color)
 
 
# ── info command ──────────────────────────────────────────────────────────────
 
@cli.command()
def info() -> None:
    """
    Show contourify version and configuration info.
 
    \b
    Example:
        contourify info
    """
    from contourify.telemetry.tracker import show_config
    from contourify.core.detector import MODEL_DIR
 
    click.echo(f"\n  contourify v{__version__}")
    click.echo(f"  Python {sys.version.split()[0]}")
    click.echo()
    click.echo("  Quick start:")
    click.echo("    contourify detect photo.jpg")
    click.echo(
        "    contourify generate photo.jpg "
        "--object 0 --text \"...\" --link https://..."
    )
    click.echo()
 
    cfg = show_config()
    click.echo(
        f"  Telemetry:   {'enabled' if cfg['telemetry_enabled'] else 'disabled'}"
    )
    click.echo(f"  Newsletter:  {cfg['newsletter_email']}")
    click.echo(f"  Config:      {cfg['config_path']}")
    click.echo(f"  Model cache: {MODEL_DIR}")
    click.echo()
 