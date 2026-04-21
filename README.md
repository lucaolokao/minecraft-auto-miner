# Minecraft Auto-Miner

External, client-side Minecraft auto-mining bot for educational/private-server testing.

## Features

- Real-time screen capture with `mss`
- HSV color-based block detection for common ores/blocks
- Auto cursor aiming and continuous mining click hold
- Live CLI status (running/mining/paused/stopped + FPS + detections)
- Global safety hotkeys (stop/pause/resume)
- JSON configuration with startup validation
- Logging and graceful shutdown

## Supported Blocks

`diamond`, `gold`, `iron`, `stone`, `deepslate`, `emerald`, `redstone`, `lapis`, `coal`, `copper`, `blackstone`, `netherite`, `obsidian`

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Or list supported blocks quickly:

```bash
python main.py --list-blocks
```

## Usage Flow

1. Open Minecraft and keep game window visible/focused.
2. Start bot (`python main.py --block diamond` or choose interactively).
3. Confirm safety prompt.
4. Use hotkeys:
   - `esc`: immediate stop
   - `f8`: pause
   - `f9`: resume

## Configuration

Edit `config.json`:

- `capture.region`: area to scan on screen
- `capture.fps_limit`: processing FPS (default 30)
- `detection.sensitivity`: color match flexibility (0.1-1.0)
- `detection.min_pixels`: minimum component size filter
- `input.move_steps`, `input.move_delay`: cursor smoothness/speed
- `input.mine_hold_seconds`: time left click stays held
- `runtime.log_level`: logging verbosity

## Project Structure

- `main.py` - CLI/menu and mining engine
- `screen_capture.py` - capture thread and frame queue
- `block_detector.py` - HSV detection + clustering
- `input_handler.py` - mouse + hotkey automation
- `config.py` - config loading/validation
- `constants.py` - blocks, color ranges, defaults
- `utils.py` - logging and helpers

## Safety Notes

- Use only in environments where automation is allowed.
- Test in private worlds/servers first.
- Keep stop hotkey accessible at all times.
