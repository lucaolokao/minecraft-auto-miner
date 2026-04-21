"""Utility helpers for logging and formatting."""

from __future__ import annotations

import logging
import time
from typing import Optional


def setup_logger(name: str, level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Create a configured logger for application modules."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def clamp(value: float, lower: float, upper: float) -> float:
    """Clamp a value between lower and upper bounds."""
    return max(lower, min(value, upper))


def now_seconds() -> float:
    """Return monotonic runtime-safe timestamp."""
    return time.monotonic()


def format_status_line(status: str, target_block: str, detections: int, fps: float) -> str:
    """Build a compact runtime status line for CLI feedback."""
    return f"Status={status} | Target={target_block} | Detections={detections} | FPS={fps:.1f}"
