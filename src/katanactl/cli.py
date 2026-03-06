"""CLI interface for katanactl."""

from __future__ import annotations

import json
import sys

import click

from .commands import (
    KatanaError,
    get_input,
    get_system_info,
    set_input,
    set_profile,
)
from .protocol import INPUT_BY_NAME, PROFILE_BY_NAME
from .transport import KatanaHID
from .volume import get_volume, set_mute, set_volume


def _json_out(data: object) -> None:
    click.echo(json.dumps(data, indent=2))


@click.group()
@click.option(
    "--device", "-d",
    default=None,
    help="HID device path (auto-detected if omitted).",
)
@click.pass_context
def main(ctx: click.Context, device: str | None) -> None:
    """Control the Creative Sound BlasterX Katana via USB."""
    ctx.ensure_object(dict)
    ctx.obj["device"] = device


def _open_hid(ctx: click.Context) -> KatanaHID:
    hid = KatanaHID(ctx.obj["device"])
    hid.open()
    return hid


# ── info ─────────────────────────────────────────────────────────────────────

@main.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """Show firmware version, serial number, and hardware ID."""
    try:
        with KatanaHID(ctx.obj["device"]) as hid:
            data = get_system_info(hid)
        _json_out(data)
    except (KatanaError, FileNotFoundError, OSError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


# ── input ────────────────────────────────────────────────────────────────────

@main.command("input")
@click.argument("source", required=False, default=None)
@click.pass_context
def input_cmd(ctx: click.Context, source: str | None) -> None:
    """Get or set the active input source.

    SOURCE can be: bluetooth, aux, optical, usb, computer
    """
    try:
        with KatanaHID(ctx.obj["device"]) as hid:
            if source is None:
                result = get_input(hid)
                _json_out({"input": result})
            else:
                result = set_input(hid, source)
                _json_out({"input": result})
    except (KatanaError, ValueError, FileNotFoundError, OSError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


# ── profile ──────────────────────────────────────────────────────────────────

@main.command()
@click.argument("name_or_number")
@click.pass_context
def profile(ctx: click.Context, name_or_number: str) -> None:
    """Switch audio profile.

    NAME_OR_NUMBER can be 0-5 or: neutral, profile-1 .. profile-4, personal
    """
    try:
        value: int | str
        if name_or_number.isdigit():
            value = int(name_or_number)
        else:
            value = name_or_number
        with KatanaHID(ctx.obj["device"]) as hid:
            result = set_profile(hid, value)
        _json_out({"profile": result})
    except (KatanaError, ValueError, FileNotFoundError, OSError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


# ── volume ───────────────────────────────────────────────────────────────────

@main.command()
@click.argument("level", required=False, default=None)
@click.option("--mute/--unmute", default=None, help="Mute or unmute speakers.")
@click.pass_context
def volume(ctx: click.Context, level: str | None, mute: bool | None) -> None:
    """Get or set speaker volume (0-100) via ALSA.

    LEVEL is a percentage (0-100). Omit to query current volume.
    """
    try:
        if mute is not None:
            result = set_mute(mute)
        elif level is not None:
            result = set_volume(int(level))
        else:
            result = get_volume()
        _json_out(result)
    except (subprocess.CalledProcessError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
