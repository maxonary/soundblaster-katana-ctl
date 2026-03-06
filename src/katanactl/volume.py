"""ALSA volume control for the Sound BlasterX Katana.

Uses amixer to get/set the 'Speakers Playback Volume' on the Katana ALSA card.
"""

from __future__ import annotations

import re
import subprocess

CARD_NAME = "Katana"
CONTROL = "Speakers"


def _run_amixer(*args: str) -> str:
    result = subprocess.run(
        ["amixer", "-c", CARD_NAME, *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def get_volume() -> dict[str, object]:
    """Return current volume percentage and mute state."""
    output = _run_amixer("sget", CONTROL)
    pct_match = re.search(r"\[(\d+)%\]", output)
    mute_match = re.search(r"\[(on|off)\]", output)
    return {
        "percent": int(pct_match.group(1)) if pct_match else None,
        "muted": mute_match.group(1) == "off" if mute_match else None,
    }


def set_volume(percent: int) -> dict[str, object]:
    """Set volume to a percentage (0-100)."""
    percent = max(0, min(100, percent))
    _run_amixer("sset", CONTROL, f"{percent}%")
    return get_volume()


def set_mute(muted: bool) -> dict[str, object]:
    """Mute or unmute speakers."""
    _run_amixer("sset", CONTROL, "mute" if muted else "unmute")
    return get_volume()
