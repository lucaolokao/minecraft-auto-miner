"""Configuration loading and validation."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict

from constants import DEFAULT_CONFIG
from utils import clamp


class ConfigError(ValueError):
    """Raised when configuration data is invalid."""


class ConfigManager:
    """Manages application configuration stored in JSON."""

    def __init__(self, config_path: str = "config.json") -> None:
        self.path = Path(config_path)
        self.config: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Load config from disk or create defaults if file is absent."""
        if not self.path.exists():
            self.config = copy.deepcopy(DEFAULT_CONFIG)
            self.save()
            return self.config

        with self.path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)

        self.config = self._merge_with_defaults(loaded)
        self.validate()
        return self.config

    def save(self) -> None:
        """Persist active configuration to disk."""
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self.config, handle, indent=2)

    def validate(self) -> None:
        """Validate and normalize important config ranges."""
        capture = self.config["capture"]
        detection = self.config["detection"]
        runtime = self.config["runtime"]
        input_cfg = self.config["input"]

        for key in ("left", "top", "width", "height"):
            if key not in capture["region"]:
                raise ConfigError(f"capture.region.{key} is required")

        if capture["region"]["width"] <= 0 or capture["region"]["height"] <= 0:
            raise ConfigError("capture.region width/height must be > 0")

        capture["fps_limit"] = int(clamp(float(capture["fps_limit"]), 1, 240))
        detection["sensitivity"] = float(clamp(float(detection["sensitivity"]), 0.1, 1.0))
        detection["min_pixels"] = int(clamp(float(detection["min_pixels"]), 1, 100000))
        detection["max_targets_per_frame"] = int(clamp(float(detection["max_targets_per_frame"]), 1, 100))

        if input_cfg["move_steps"] <= 0:
            raise ConfigError("input.move_steps must be > 0")
        if input_cfg["move_delay"] < 0:
            raise ConfigError("input.move_delay cannot be negative")
        if input_cfg["mine_hold_seconds"] < 0:
            raise ConfigError("input.mine_hold_seconds cannot be negative")

        if runtime["idle_sleep_seconds"] < 0:
            raise ConfigError("runtime.idle_sleep_seconds cannot be negative")

    def _merge_with_defaults(self, loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config over defaults recursively."""
        merged = copy.deepcopy(DEFAULT_CONFIG)

        def _merge(base: Dict[str, Any], incoming: Dict[str, Any]) -> None:
            for key, value in incoming.items():
                if isinstance(value, dict) and isinstance(base.get(key), dict):
                    _merge(base[key], value)
                else:
                    base[key] = value

        _merge(merged, loaded)
        return merged
