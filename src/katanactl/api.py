"""FastAPI REST-API for the Sound BlasterX Katana."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .commands import (
    KatanaError,
    get_input,
    get_system_info,
    set_input,
    set_profile,
)
from .protocol import INPUT_BY_NAME, PROFILE_BY_NAME
from .transport import KatanaHID, find_hidraw_device
from .volume import get_volume, set_mute, set_volume

app = FastAPI(
    title="katanactl API",
    description="REST API for controlling the Creative Sound BlasterX Katana",
    version="0.1.0",
)


@contextmanager
def _hid() -> Generator[KatanaHID, None, None]:
    try:
        with KatanaHID() as hid:
            yield hid
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except KatanaError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except OSError as exc:
        raise HTTPException(status_code=503, detail=f"HID I/O error: {exc}")


# ── Models ───────────────────────────────────────────────────────────────────

class InputRequest(BaseModel):
    source: str = Field(
        ...,
        description="Input source name",
        examples=["computer", "bluetooth", "aux", "optical", "usb"],
    )


class ProfileRequest(BaseModel):
    profile: str | int = Field(
        ...,
        description="Profile name or number (0-5)",
        examples=["neutral", 0, "profile-1", 3],
    )


class VolumeRequest(BaseModel):
    percent: int = Field(..., ge=0, le=100, description="Volume 0-100")


class MuteRequest(BaseModel):
    muted: bool


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/info")
def api_info() -> dict:
    """Get system info (firmware, serial, hardware ID)."""
    with _hid() as hid:
        return get_system_info(hid)


@app.get("/input")
def api_get_input() -> dict:
    """Get the currently active input source."""
    with _hid() as hid:
        return {"input": get_input(hid)}


@app.post("/input")
def api_set_input(req: InputRequest) -> dict:
    """Switch the active input source."""
    try:
        with _hid() as hid:
            result = set_input(hid, req.source)
        return {"input": result}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.post("/profile")
def api_set_profile(req: ProfileRequest) -> dict:
    """Switch audio profile."""
    try:
        with _hid() as hid:
            result = set_profile(hid, req.profile)
        return {"profile": result}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.get("/volume")
def api_get_volume() -> dict:
    """Get current volume level and mute state."""
    return get_volume()


@app.post("/volume")
def api_set_volume(req: VolumeRequest) -> dict:
    """Set volume level (0-100)."""
    return set_volume(req.percent)


@app.post("/mute")
def api_set_mute(req: MuteRequest) -> dict:
    """Mute or unmute speakers."""
    return set_mute(req.muted)


@app.get("/health")
def api_health() -> dict:
    """Health check -- verifies the Katana HID device is reachable."""
    try:
        device = find_hidraw_device()
        return {"status": "ok", "device": device}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
