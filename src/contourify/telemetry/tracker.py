"""
    contourify/telemetry/tracker.py — Anonymous opt-in usage telemetry.
 
    PRIVACY CONTRACT (never violated):
      ✅ Opt-in only     — user asked once on first run, never silently enabled
      ✅ Anonymous       — no image paths, no file contents, no personal data
      ✅ Fire-and-forget — 3s timeout, never blocks, never crashes
      ✅ Transparent     — user can inspect or disable at any time
 
    What IS sent (with consent):
      - Event type (detect, generate, cli_run etc.)
      - Platform (win32 / linux / darwin)
      - Python version (major.minor only)
      - contourify version
      - Approximate country/city (from ipinfo.io)
 
    What is NEVER sent:
      - Image paths or contents
      - SVG output
      - Any personally identifying information
 
    User controls:
      contourify --telemetry on
      contourify --telemetry off
      contourify --telemetry status
 
    Config stored at: ~/.contourify/config.json
"""
 
from __future__ import annotations
 
import json
import pathlib
import platform
import sys
import threading
import urllib.request
from datetime import datetime, timezone
from typing import Optional
 
 
# ── Constants ─────────────────────────────────────────────────────────────────
TELEMETRY_BASE  = "https://api.vickkykruzprogramming.dev/api"
TRACK_URL       = f"{TELEMETRY_BASE}/track"
ACTIVITY_URL    = f"{TELEMETRY_BASE}/activity"
SUBSCRIBE_URL   = f"{TELEMETRY_BASE}/subscribe"
 
CONFIG_DIR      = pathlib.Path.home() / ".contourify"
CONFIG_FILE     = CONFIG_DIR / "config.json"
TIMEOUT_SECONDS = 3
try:
    from importlib.metadata import version as _pkg_version
    VERSION = _pkg_version("contourify")
except Exception:
    VERSION = "0.1.0"
 
# Location cache — ipinfo.io called at most once per session
_location_cache: dict = {}
 
 
# ── Config helpers ────────────────────────────────────────────────────────────
 
def _load_config() -> dict:
    try:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}
 
 
def _save_config(cfg: dict) -> None:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(cfg, indent=2), encoding="utf-8"
        )
    except Exception:
        pass
 
 
def is_telemetry_enabled() -> bool:
    return _load_config().get("telemetry", False)
 
 
def is_first_run() -> bool:
    """True if the user has never been asked about telemetry."""
    return "telemetry" not in _load_config()
 
 
def set_telemetry(enabled: bool) -> None:
    cfg = _load_config()
    cfg["telemetry"] = enabled
    _save_config(cfg)
 
 
def get_subscribed_email() -> Optional[str]:
    return _load_config().get("newsletter_email")
 
 
def set_subscribed_email(email: str) -> None:
    cfg = _load_config()
    cfg["newsletter_email"] = email
    _save_config(cfg)
 
 
# ── Location lookup ───────────────────────────────────────────────────────────
 
def _get_location() -> dict:
    """
    Get approximate location from ipinfo.io.
    Cached after first call — only one lookup per session.
    Returns safe defaults if the call fails or times out.
    """
    global _location_cache
    if _location_cache:
        return _location_cache
 
    defaults = {
        "country":      "Unknown",
        "country_code": "XX",
        "city":         "Unknown",
    }
    try:
        req = urllib.request.Request(
            "https://ipinfo.io/json",
            headers={"Accept": "application/json"},
        )
        raw  = urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS).read()
        data = json.loads(raw)
        _location_cache = {
            "country":      data.get("country", "XX"),
            "country_code": data.get("country", "XX"),
            "city":         data.get("city", "Unknown"),
        }
        return _location_cache
    except Exception:
        return defaults
 
 
# ── Low-level HTTP helpers ────────────────────────────────────────────────────
 
def _post(url: str, payload: dict) -> None:
    """Synchronous POST. Silently swallows all errors."""
    try:
        body = json.dumps(payload).encode("utf-8")
        req  = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS)
    except Exception:
        pass
 
 
def _fire(url: str, payload: dict) -> None:
    """Background-thread POST. Never blocks. Never raises."""
    t = threading.Thread(target=_post, args=(url, payload), daemon=True)
    t.start()
 
 
# ── First-run consent prompt ──────────────────────────────────────────────────
 
def prompt_first_run() -> None:
    """
    Show the opt-in prompt on first run.
    Never shown again after the user responds.
    """
    if not is_first_run():
        return
 
    print()
    print("─" * 55)
    print("  Welcome to contourify v0.1.0 👋")
    print()
    print("  Help improve contourify by sharing anonymous")
    print("  usage data. This includes only:")
    print("    • Which features you use (detect, generate, etc.)")
    print("    • Your platform and Python version")
    print("    • Approximate country (no IPs stored)")
    print()
    print("  Your images, file paths, and SVG output")
    print("  are NEVER collected.")
    print()
 
    try:
        answer = input(
            "  Allow anonymous telemetry? [y/N]: "
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = "n"
 
    opted_in = answer in ("y", "yes")
    set_telemetry(opted_in)
 
    if opted_in:
        print()
        print("  Thanks! One more thing — want to be notified")
        print("  about new contourify features and updates?")
        print()
        try:
            email = input(
                "  Your email (or press Enter to skip): "
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            email = ""
 
        if email and "@" in email and "." in email:
            set_subscribed_email(email)
            _post(SUBSCRIBE_URL, {
                "email":  email,
                "source": "contourify_cli",
            })
            print(f"  ✅ Subscribed! We'll notify you at {email}")
        else:
            print("  Skipped — you can subscribe later at:")
            print("  https://vickkykruzprogramming.dev")
 
        print()
        print("  You can change this setting any time:")
        print("  contourify --telemetry off")
 
        # Log install event synchronously
        loc = _get_location()
        _post(ACTIVITY_URL, {
            "type":         "tool_installed",
            "source":       "contourify_cli",
            "page":         "/cli/install",
            "country":      loc["country"],
            "country_code": loc["country_code"],
            "city":         loc["city"],
            "meta": {
                "tool":     "contourify",
                "version":  VERSION,
                "platform": sys.platform,
                "python": (
                    f"{sys.version_info.major}"
                    f".{sys.version_info.minor}"
                ),
            },
        })
        _post(TRACK_URL, {
            "page":         "/cli/install",
            "country":      loc["country"],
            "country_code": loc["country_code"],
            "city":         loc["city"],
        })
 
    else:
        print()
        print("  No problem — telemetry stays off.")
        print("  You can enable it later: contourify --telemetry on")
 
    print("─" * 55)
    print()
 
 
# ── Telemetry management ──────────────────────────────────────────────────────
 
def handle_telemetry_flag(value: str) -> None:
    """Handle --telemetry on/off/status from CLI."""
    value = value.strip().lower()
 
    if value == "on":
        set_telemetry(True)
        print("✅ Telemetry enabled. Thank you for helping improve contourify!")
        if not get_subscribed_email():
            try:
                email = input(
                    "Want update notifications? Enter email "
                    "(or Enter to skip): "
                ).strip().lower()
                if email and "@" in email and "." in email:
                    set_subscribed_email(email)
                    _post(SUBSCRIBE_URL, {
                        "email":  email,
                        "source": "contourify_cli",
                    })
                    print(f"✅ Subscribed at {email}")
            except (EOFError, KeyboardInterrupt):
                pass
 
    elif value == "off":
        set_telemetry(False)
        print("✅ Telemetry disabled.")
 
    elif value == "status":
        cfg     = _load_config()
        enabled = cfg.get("telemetry", False)
        email   = cfg.get("newsletter_email", "not set")
        print(f"  Telemetry:  {'enabled' if enabled else 'disabled'}")
        print(f"  Newsletter: {email}")
        print(f"  Config at:  {CONFIG_FILE}")
 
    else:
        print(f"Unknown value '{value}'. Use: on | off | status")
 
 
# ── Event tracking ────────────────────────────────────────────────────────────
 
def track_event(event: str, metadata: Optional[dict] = None) -> None:
    """
    Send an anonymous usage event if telemetry is enabled.
 
    Args:
        event:    Event name e.g. "contourify_detect", "contourify_generate", "contourify_run".
        metadata: Optional extra data. Must not contain
                  personal data or file paths.
    """
    if not is_telemetry_enabled():
        return
 
    def _do() -> None:
        loc = _get_location()
        _post(ACTIVITY_URL, {
            "type":         event,
            "source":       "contourify_cli",
            "page":         f"/cli/{event}",
            "country":      loc["country"],
            "country_code": loc["country_code"],
            "city":         loc["city"],
            "meta": {
                "tool":     "contourify",
                "version":  VERSION,
                "platform": sys.platform,
                "python": (
                    f"{sys.version_info.major}"
                    f".{sys.version_info.minor}"
                ),
                **(metadata or {}),
            },
        })
        _post(TRACK_URL, {
            "page":         f"/cli/{event}",
            "country":      loc["country"],
            "country_code": loc["country_code"],
            "city":         loc["city"],
        })
 
    threading.Thread(target=_do, daemon=True).start()
 
 
def track_detect(objects_found: int) -> None:
    """Called when detect completes."""
    track_event("contourify_detect", {"objects_found": objects_found})
 
 
def track_generate(color: str) -> None:
    """Called when generate completes."""
    track_event("contourify_generate", {"color": color})
 
 
def track_cli_run(command: str) -> None:
    """Called when CLI command runs."""
    track_event("contourify_run", {"command": command})
 
 
def show_config() -> dict:
    """
    Return current telemetry configuration.
 
    Returns:
        Dict with telemetry_enabled, first_run_done,
        session_id, newsletter_email and config_path keys.
 
    Example:
        from contourify.telemetry.tracker import show_config
        print(show_config())
    """
    config = _load_config()
    return {
        "telemetry_enabled": config.get("telemetry",       False),
        "first_run_done":    config.get("first_run_done",  False),
        "session_id":        config.get("session_id",      "not set"),
        "newsletter_email":  config.get("newsletter_email","not set"),
        "config_path":       str(CONFIG_FILE),
    }