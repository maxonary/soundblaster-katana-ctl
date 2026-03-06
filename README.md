# soundblaster-katana-ctl

Control the **Creative Sound BlasterX Katana** soundbar from Linux via USB HID.

Provides a CLI tool, a REST API, and Home Assistant integration for:

- Querying system info (firmware version, serial number)
- Switching input sources (Bluetooth, AUX, Optical, USB, Computer)
- Changing audio profiles (Neutral, Profile 1–4, Personal)
- Controlling volume and mute via ALSA

## Requirements

- Raspberry Pi (or any Linux machine) with the Katana connected via USB
- Python 3.10+
- The Katana exposes two HID interfaces; this tool uses the 64-byte control interface (`/dev/hidrawN`, interface 4)

## Installation

```bash
cd /home/pi/soundblaster-katana-ctl
pip install -e .
```

### udev rule (optional, for non-root access)

```bash
sudo cp udev/99-katana.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## CLI Usage

```bash
# System info
katanactl info

# Query current input
katanactl input

# Switch input
katanactl input computer
katanactl input bluetooth
katanactl input aux
katanactl input optical
katanactl input usb

# Switch profile (0-5 or name)
katanactl profile neutral
katanactl profile 2
katanactl profile personal

# Volume control (via ALSA)
katanactl volume          # query
katanactl volume 75       # set to 75%
katanactl volume --mute   # mute
katanactl volume --unmute # unmute
```

## REST API

Start the API server:

```bash
uvicorn katanactl.api:app --host 0.0.0.0 --port 8099
```

Or install as a systemd service:

```bash
sudo cp systemd/katanactl-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now katanactl-api
```

### Endpoints

| Method | Path       | Description                |
|--------|------------|----------------------------|
| GET    | `/info`    | System info                |
| GET    | `/input`   | Current input source       |
| POST   | `/input`   | Set input source           |
| POST   | `/profile` | Switch profile             |
| GET    | `/volume`  | Current volume & mute      |
| POST   | `/volume`  | Set volume (0-100)         |
| POST   | `/mute`    | Mute/unmute                |
| GET    | `/health`  | Health check               |

Interactive docs at `http://<host>:8099/docs`.

## Home Assistant

Copy `homeassistant/katana.yaml` and include it in your HA configuration. Replace `KATANA_HOST` with the Pi's IP address. See the file for sensor, input_select, and automation examples.

## Protocol Reference

Based on the reverse-engineered USB HID protocol documented at [therion23/KatanaHacking](https://github.com/therion23/KatanaHacking).

Command frame: `[0x5A] [cmd] [len] [payload...]` — responses are 64 bytes, zero-padded, same structure.

## License

MIT
