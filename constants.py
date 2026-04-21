"""Project-wide constants for Minecraft Auto-Miner."""

from __future__ import annotations

from typing import Dict, List, Tuple

HSVRange = Tuple[Tuple[int, int, int], Tuple[int, int, int]]

SUPPORTED_BLOCKS: List[str] = [
    "diamond",
    "gold",
    "iron",
    "stone",
    "deepslate",
    "emerald",
    "redstone",
    "lapis",
    "coal",
    "copper",
    "blackstone",
    "netherite",
    "obsidian",
]

# HSV scale is 0-255 for all channels.
# Ranges are intentionally broad to support varied shaders/lighting.
BLOCK_HSV_RANGES: Dict[str, List[HSVRange]] = {
    "diamond": [((110, 40, 80), (140, 255, 255))],
    "gold": [((20, 90, 90), (40, 255, 255))],
    "iron": [((0, 0, 120), (255, 60, 255))],
    "stone": [((0, 0, 70), (255, 55, 185))],
    "deepslate": [((110, 10, 25), (180, 90, 120))],
    "emerald": [((55, 90, 80), (95, 255, 255))],
    "redstone": [((0, 120, 70), (15, 255, 255)), ((235, 120, 70), (255, 255, 255))],
    "lapis": [((140, 90, 50), (180, 255, 255))],
    "coal": [((0, 0, 0), (255, 80, 70))],
    "copper": [((10, 70, 70), (28, 255, 255))],
    "blackstone": [((170, 10, 10), (255, 110, 80))],
    "netherite": [((0, 0, 20), (255, 50, 85))],
    "obsidian": [((175, 40, 10), (255, 255, 100))],
}

DEFAULT_CONFIG = {
    "capture": {
        "region": {"left": 0, "top": 0, "width": 1280, "height": 720},
        "fps_limit": 30,
    },
    "detection": {
        "sensitivity": 0.8,
        "min_pixels": 80,
        "max_targets_per_frame": 5,
    },
    "input": {
        "move_steps": 15,
        "move_delay": 0.004,
        "mine_hold_seconds": 0.4,
        "hotkeys": {
            "stop": "esc",
            "pause": "f8",
            "resume": "f9",
        },
    },
    "runtime": {
        "idle_sleep_seconds": 0.03,
        "show_visual_feedback": True,
        "log_level": "INFO",
    },
    "logging": {
        "file": "bot.log",
    },
}

STATUS_RUNNING = "Running"
STATUS_MINING = "Mining"
STATUS_PAUSED = "Paused"
STATUS_STOPPED = "Stopped"
