"""Katana USB HID protocol constants.

Reference: https://github.com/therion23/KatanaHacking/blob/master/USB.md

Command frame: [0x5A] [cmd] [len] [payload...]
Response frame: same structure, zero-padded to 64 bytes.
"""

# ── Command opcodes ──────────────────────────────────────────────────────────

CMD_ERROR = 0x02
CMD_SYSTEM_INFO = 0x07
CMD_EQ_GET = 0x11
CMD_EQ_SET = 0x12
CMD_PROFILE = 0x1A
CMD_VOLUME = 0x23
CMD_LIGHTING = 0x3A
CMD_INPUT = 0x9C

# ── System-info sub-requests (payload byte 0) ───────────────────────────────

SYSINFO_HW = 0x00
SYSINFO_FIRMWARE = 0x02
SYSINFO_SERIAL = 0x03

# ── Input sources (CMD_INPUT subcommand 0x00, byte 1) ───────────────────────

INPUT_BLUETOOTH = 0x01
INPUT_AUX = 0x04
INPUT_OPTICAL = 0x07
INPUT_USB_STORAGE = 0x09
INPUT_USB_COMPUTER = 0x0C

INPUT_NAMES: dict[int, str] = {
    INPUT_BLUETOOTH: "bluetooth",
    INPUT_AUX: "aux",
    INPUT_OPTICAL: "optical",
    INPUT_USB_STORAGE: "usb",
    INPUT_USB_COMPUTER: "computer",
}

INPUT_BY_NAME: dict[str, int] = {v: k for k, v in INPUT_NAMES.items()}

# ── Input sub-commands ───────────────────────────────────────────────────────

INPUT_SUB_SET = 0x00
INPUT_SUB_QUERY = 0x01

# ── Profile numbers ─────────────────────────────────────────────────────────

PROFILE_NEUTRAL = 0
PROFILE_PERSONAL = 5

PROFILE_NAMES: dict[int, str] = {
    0: "neutral",
    1: "profile-1",
    2: "profile-2",
    3: "profile-3",
    4: "profile-4",
    5: "personal",
}

PROFILE_BY_NAME: dict[str, int] = {v: k for k, v in PROFILE_NAMES.items()}
