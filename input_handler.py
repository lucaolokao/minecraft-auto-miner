"""Keyboard and mouse automation helpers."""

from __future__ import annotations

import time
from typing import Callable, Optional, Tuple


class InputHandler:
    """Handle automated mouse movement, mining clicks, and hotkeys."""

    def __init__(self) -> None:
        self.mouse = None
        self._button_left = None
        self._input_available = False
        self._hotkey_backend = None
        self._registered_hotkeys = []

        try:
            from pynput.mouse import Button, Controller as MouseController
        except Exception:
            return

        self.mouse = MouseController()
        self._button_left = Button.left
        self._input_available = True

    def move_to(self, target: Tuple[int, int], steps: int = 15, delay: float = 0.004) -> None:
        """Move cursor smoothly to the requested absolute position."""
        if not self._input_available:
            raise RuntimeError("Mouse input backend unavailable on this platform/environment")
        start_x, start_y = self.mouse.position
        end_x, end_y = target
        steps = max(1, int(steps))

        for index in range(1, steps + 1):
            ratio = index / steps
            x = int(start_x + (end_x - start_x) * ratio)
            y = int(start_y + (end_y - start_y) * ratio)
            self.mouse.position = (x, y)
            if delay > 0:
                time.sleep(delay)

    def hold_mine(self, duration_seconds: float) -> None:
        """Hold left click for duration to simulate continuous mining."""
        if not self._input_available:
            raise RuntimeError("Mouse input backend unavailable on this platform/environment")
        self.mouse.press(self._button_left)
        time.sleep(max(0.0, duration_seconds))
        self.mouse.release(self._button_left)

    def register_hotkeys(
        self,
        stop_key: str,
        pause_key: str,
        resume_key: str,
        on_stop: Callable[[], None],
        on_pause: Callable[[], None],
        on_resume: Callable[[], None],
    ) -> None:
        """Register global hotkeys using keyboard package when available."""
        try:
            import keyboard
        except Exception:
            self._hotkey_backend = None
            return

        self._hotkey_backend = keyboard
        self._registered_hotkeys.append(keyboard.add_hotkey(stop_key, on_stop))
        self._registered_hotkeys.append(keyboard.add_hotkey(pause_key, on_pause))
        self._registered_hotkeys.append(keyboard.add_hotkey(resume_key, on_resume))

    def unregister_hotkeys(self) -> None:
        """Unregister all configured hotkeys."""
        if not self._hotkey_backend:
            return

        for handle in self._registered_hotkeys:
            try:
                self._hotkey_backend.remove_hotkey(handle)
            except Exception:
                pass
        self._registered_hotkeys.clear()

    @property
    def input_available(self) -> bool:
        """Whether the mouse automation backend is available."""
        return self._input_available
