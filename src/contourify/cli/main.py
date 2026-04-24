"""
    contourify CLI - Command line interface.
 
    Usage:
        contourify help
        contourify detect IMAGE
        contourify generate IMAGE --object 0 --text "My Product" --link https://example.com
        contourify generate IMAGE --object 0 --text "My Product" --link https://example.com --format html
        contourify generate IMAGE --object 0 --text "My Product" --link https://example.com --label "Deer"
        contourify models list
        contourify models set yolov8s
        contourify models download yolov8s
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
    Getting started:
        contourify help
 
    \b
    Quick example:
        contourify detect photo.jpg
        contourify generate photo.jpg --object 0 --text "My Chair" --link https://example.com
 
    \b
    Telemetry:
        contourify --telemetry status
        contourify --telemetry off
    """
    if telemetry is not None:
        handle_telemetry_flag(telemetry)
        ctx.exit()
 
    prompt_first_run()
 
 
# ── help command ──────────────────────────────────────────────────────────────
 
@cli.command(name="help")
def help_command() -> None:
    """
    Show the full getting started guide with examples.
 
    \b
    Example:
        contourify help
    """
    click.echo(f"""
  contourify v{__version__} — Getting Started Guide
  {"─" * 48}
 
  contourify turns any image into an interactive SVG
  where detected objects show a popup card on hover
  with your custom text and a clickable link.
 
  {"─" * 48}
  STEP 1 — Detect objects in your image
  {"─" * 48}
 
    contourify detect photo.jpg
 
  This lists all detected objects with their ID,
  label and confidence score.
 
  {"─" * 48}
  STEP 2 — Generate your interactive file
  {"─" * 48}
 
    contourify generate photo.jpg \\
        --object 0 \\
        --text "Handcrafted Oak Chair" \\
        --link https://shop.example.com/chair
 
  Output: photo_contourify.svg in the same folder.
  Open it in any browser to see the hotspot.
 
  {"─" * 48}
  OPTIONS
  {"─" * 48}
 
    --format html     Full-screen HTML — no white space
                      when opening locally in a browser.
 
    --label "Deer"    Override a misdetected label.
                      Use when the model gets it wrong.
 
    --color "#27c97a" Custom highlight color (hex).
                      Default is blue (#3b82f6).
 
    --output path     Custom output file path.
 
    --model yolov8s   Use a more accurate model.
                      See: contourify models list
 
  {"─" * 48}
  EXAMPLES
  {"─" * 48}
 
    # HTML output (no white space locally)
    contourify generate photo.jpg \\
        --object 0 --text "My Product" \\
        --link https://example.com --format html
 
    # Override misdetected label
    contourify generate photo.jpg \\
        --object 0 --text "Fallow Deer" \\
        --link https://example.com --label "Deer"
 
    # Custom color and output path
    contourify generate photo.jpg \\
        --object 1 --text "Sony Camera" \\
        --link https://example.com \\
        --color "#27c97a" --output camera.svg
 
    # Use a more accurate model
    contourify generate photo.jpg \\
        --object 0 --text "My Chair" \\
        --link https://example.com \\
        --model yolov8s-seg.pt
 
  {"─" * 48}
  MODELS
  {"─" * 48}
 
    contourify models list          List available models
    contourify models set yolov8s   Set default model
    contourify models download all  Pre-download all models
 
  {"─" * 48}
  MORE
  {"─" * 48}
 
    contourify info                 Version and config
    contourify --telemetry status   Telemetry settings
    contourify --version            Version number
 
    Full docs: https://github.com/vickkykruz/contourify
""")
 
 
# ── models command group ──────────────────────────────────────────────────────
 
@cli.group()
def models() -> None:
    """
    Manage detection models.
 
    \b
    Commands:
        contourify models list
        contourify models set yolov8s
        contourify models download yolov8s
        contourify models download all
    """
    pass
 
 
@models.command(name="list")
def models_list() -> None:
    """
    List all available YOLO models with size and accuracy.
 
    \b
    Example:
        contourify models list
    """
    from contourify.adapters.yolo import YOLO_MODELS
    from contourify.core.detector import MODEL_DIR
    from contourify.telemetry.tracker import _load_config
 
    cfg           = _load_config()
    default_model = cfg.get("default_model", "yolov8n-seg.pt")
 
    click.echo(f"\n  Available models:\n")
    click.echo(
        f"  {'Name':<22} {'Size':<10} {'Speed':<12} {'Accuracy':<12}"
    )
    click.echo(
        f"  {'─' * 22} {'─' * 10} {'─' * 12} {'─' * 12}"
    )
 
    for name, info in YOLO_MODELS.items():
        marker = " <- default" if name == default_model else ""
        click.echo(
            f"  {name:<22} {info['size']:<10} "
            f"{info['speed']:<12} {info['accuracy']:<12}{marker}"
        )
 
    click.echo()
    click.echo(f"  Default model: {default_model}")
    click.echo(f"  Cache location: {MODEL_DIR}")
    click.echo()
    click.echo("  To change default:")
    click.echo("    contourify models set yolov8s")
    click.echo()
    click.echo("  To pre-download a model:")
    click.echo("    contourify models download yolov8s")
    click.echo()
 
 
@models.command(name="set")
@click.argument("model_name")
def models_set(model_name: str) -> None:
    """
    Set the default model used by contourify.
 
    MODEL_NAME can be a short name (yolov8s) or full name
    (yolov8s-seg.pt) or an absolute path to a custom .pt file.
 
    \b
    Examples:
        contourify models set yolov8s
        contourify models set yolov8m
        contourify models set /path/to/my_custom_model.pt
    """
    from contourify.adapters.yolo import YOLO_MODELS
    from contourify.telemetry.tracker import _load_config, _save_config
 
    # Normalise short names
    if not model_name.endswith(".pt") and not os.path.isabs(model_name):
        model_name = f"{model_name}-seg.pt"
 
    # Validate — must be a known model or an existing file path
    is_known  = model_name in YOLO_MODELS
    is_custom = os.path.isabs(model_name) and os.path.exists(model_name)
 
    if not is_known and not is_custom:
        click.echo(f"\n  Unknown model: {model_name}")
        click.echo()
        click.echo("  Available built-in models:")
        for name in YOLO_MODELS:
            click.echo(f"    {name}")
        click.echo()
        click.echo(
            "  To use a custom model provide the full path:\n"
            "    contourify models set /path/to/my_model.pt"
        )
        sys.exit(1)
 
    cfg = _load_config()
    cfg["default_model"] = model_name
    _save_config(cfg)
 
    click.echo(f"\n  Default model set to: {model_name}")
    if is_custom:
        click.echo("  Custom model path saved.")
    click.echo()
 
 
@models.command(name="download")
@click.argument("model_name")
def models_download(model_name: str) -> None:
    """
    Pre-download a model to the local cache.
 
    MODEL_NAME can be a short name (yolov8s), full name
    (yolov8s-seg.pt) or 'all' to download every built-in model.
 
    \b
    Examples:
        contourify models download yolov8s
        contourify models download yolov8m
        contourify models download all
    """
    from contourify.adapters.yolo import YOLO_MODELS, YOLODetector
    from contourify.core.detector import MODEL_DIR
 
    # Resolve model list
    if model_name.lower() == "all":
        to_download = list(YOLO_MODELS.keys())
    else:
        if not model_name.endswith(".pt"):
            model_name = f"{model_name}-seg.pt"
        if model_name not in YOLO_MODELS:
            click.echo(f"\n  Unknown model: {model_name}")
            click.echo("  Run 'contourify models list' to see available models.")
            sys.exit(1)
        to_download = [model_name]
 
    click.echo()
    for name in to_download:
        cached = MODEL_DIR / name
        if cached.exists():
            click.echo(f"  {name} — already cached, skipping.")
            continue
 
        click.echo(f"  Downloading {name}...")
        try:
            detector = YOLODetector(model=name)
            detector._load_model()
            click.echo(f"  {name} — downloaded successfully.")
        except Exception as e:
            click.echo(f"  {name} — failed: {e}", err=True)
 
    click.echo()
    click.echo(f"  Models cached at: {MODEL_DIR}")
    click.echo()
 
 
# ── detect command ────────────────────────────────────────────────────────────
 
@cli.command()
@click.argument("image", type=click.Path(exists=True))
@click.option(
    "--model", "-m",
    default=None,
    help=(
        "YOLOv8 model to use. Defaults to the model set by "
        "'contourify models set' or yolov8n-seg.pt."
    ),
)
@click.option(
    "--conf", "-c",
    default=0.25,
    show_default=True,
    type=float,
    help="Minimum confidence threshold (0-1).",
)
def detect(image: str, model: str | None, conf: float) -> None:
    """
    Detect all objects in an IMAGE.
 
    \b
    Examples:
        contourify detect photo.jpg
        contourify detect photo.jpg --conf 0.15
        contourify detect photo.jpg --model yolov8s-seg.pt
 
    \b
    Supported objects (80 COCO classes):
        People, animals (cat, dog, horse, cow, sheep, bird,
        elephant, bear, zebra, giraffe), vehicles, furniture,
        electronics, food, sports equipment and more.
    """
    track_cli_run("detect")
 
    # Use default model from config if not specified
    if model is None:
        from contourify.telemetry.tracker import _load_config
        model = _load_config().get("default_model", "yolov8n-seg.pt")
 
    click.echo(f"\n  Detecting objects in: {os.path.basename(image)}")
    click.echo(f"  Model: {model}\n")
 
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
            "  Note: contourify detects 80 common object types."
        )
        click.echo(
            "  Uncommon subjects like wildlife may not be recognised."
        )
        return
 
    click.echo(f"  Found {len(objects)} object(s):\n")
    click.echo(f"  {'ID':<6} {'Label':<20} {'Confidence':<12}")
    click.echo(f"  {'─' * 6} {'─' * 20} {'─' * 12}")
 
    for obj in objects:
        click.echo(
            f"  {obj.id:<6} {obj.label.capitalize():<20} {obj.score_pct:<12}"
        )
 
    low_conf = [o for o in objects if o.score < 0.4]
    if low_conf:
        click.echo()
        click.echo("  Warning: Some detections have low confidence.")
        click.echo(
            "  Use --label to override the displayed label:"
        )
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
    help="ID of the detected object to annotate.",
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
        "Example: --label \"Deer\" when YOLO says Sheep."
    ),
)
@click.option(
    "--format", "fmt",
    default="svg",
    show_default=True,
    type=click.Choice(["svg", "html"], case_sensitive=False),
    help=(
        "'svg' (default) or 'html'. "
        "Use html to eliminate white space when opening locally."
    ),
)
@click.option(
    "--output",
    default=None,
    help="Output file path. Defaults to <image>_contourify.svg",
)
@click.option(
    "--model", "-m",
    default=None,
    help="YOLOv8 model to use. Defaults to configured default model.",
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
    model:     str | None,
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
    For full options run: contourify help
    """
    track_cli_run("generate")
 
    # Use default model from config if not specified
    if model is None:
        from contourify.telemetry.tracker import _load_config
        model = _load_config().get("default_model", "yolov8n-seg.pt")
 
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
    click.echo(f"  Model:      {model}")
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
    from contourify.telemetry.tracker import show_config, _load_config
    from contourify.core.detector import MODEL_DIR
 
    cfg           = _load_config()
    default_model = cfg.get("default_model", "yolov8n-seg.pt")
 
    click.echo(f"\n  contourify v{__version__}")
    click.echo(f"  Python {sys.version.split()[0]}")
    click.echo()
    click.echo("  Quick start:")
    click.echo("    contourify help")
    click.echo("    contourify detect photo.jpg")
    click.echo(
        "    contourify generate photo.jpg "
        "--object 0 --text \"...\" --link https://..."
    )
    click.echo()
 
    telemetry_cfg = show_config()
    click.echo(
        f"  Telemetry:     "
        f"{'enabled' if telemetry_cfg['telemetry_enabled'] else 'disabled'}"
    )
    click.echo(f"  Newsletter:    {telemetry_cfg['newsletter_email']}")
    click.echo(f"  Config:        {telemetry_cfg['config_path']}")
    click.echo(f"  Model cache:   {MODEL_DIR}")
    click.echo(f"  Default model: {default_model}")
    click.echo()
    click.echo("  To see available models:")
    click.echo("    contourify models list")
    click.echo()
 