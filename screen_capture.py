"""Real-time screen capture service."""

from __future__ import annotations

import threading
import time
from queue import Full, Queue
from typing import Dict, Optional

import numpy as np


class ScreenCapture:
    """Capture frames from a configured region with FPS limiting."""

    def __init__(self, region: Dict[str, int], fps_limit: int = 30) -> None:
        self.region = region
        self.fps_limit = max(1, fps_limit)
        self._frame_queue: "Queue[np.ndarray]" = Queue(maxsize=2)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start capture thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop capture thread."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)

    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Return most recent frame if available."""
        frame = None
        while not self._frame_queue.empty():
            frame = self._frame_queue.get_nowait()
        return frame

    def _run(self) -> None:
        frame_delay = 1.0 / self.fps_limit
        try:
            import mss
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("mss is required for screen capture") from exc

        with mss.mss() as sct:
            monitor = {
                "left": int(self.region["left"]),
                "top": int(self.region["top"]),
                "width": int(self.region["width"]),
                "height": int(self.region["height"]),
            }
            while not self._stop_event.is_set():
                start = time.monotonic()
                shot = sct.grab(monitor)
                frame = np.array(shot, dtype=np.uint8)[..., :3]
                frame = frame[..., ::-1]  # BGR -> RGB

                try:
                    self._frame_queue.put_nowait(frame)
                except Full:
                    try:
                        _ = self._frame_queue.get_nowait()
                    except Exception:
                        pass
                    self._frame_queue.put_nowait(frame)

                elapsed = time.monotonic() - start
                if elapsed < frame_delay:
                    time.sleep(frame_delay - elapsed)
