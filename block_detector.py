"""Color-based block detection from captured frames."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import List, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw

from constants import BLOCK_HSV_RANGES


@dataclass(frozen=True)
class Detection:
    """Represents one detected target in frame coordinates."""

    center: Tuple[int, int]
    bbox: Tuple[int, int, int, int]
    pixels: int


class BlockDetector:
    """Detect configured block colors using HSV masks and component filtering."""

    def __init__(self, sensitivity: float = 0.8, min_pixels: int = 80) -> None:
        self.sensitivity = float(np.clip(sensitivity, 0.1, 1.0))
        self.min_pixels = max(1, int(min_pixels))

    def detect_blocks(self, frame_rgb: np.ndarray, block_name: str) -> List[Detection]:
        """Detect target block positions in an RGB frame."""
        if block_name not in BLOCK_HSV_RANGES:
            raise ValueError(f"Unsupported block: {block_name}")

        hsv = self._rgb_to_hsv_255(frame_rgb)
        mask = np.zeros(hsv.shape[:2], dtype=bool)

        for low, high in BLOCK_HSV_RANGES[block_name]:
            adjusted_low, adjusted_high = self._adjust_range(low, high)
            local = np.all(hsv >= adjusted_low, axis=2) & np.all(hsv <= adjusted_high, axis=2)
            mask |= local

        detections = self._connected_components(mask)
        detections.sort(key=lambda item: item.pixels, reverse=True)
        return detections

    def annotate_frame(self, frame_rgb: np.ndarray, detections: Sequence[Detection]) -> np.ndarray:
        """Return frame with visual detection markers."""
        image = Image.fromarray(frame_rgb)
        draw = ImageDraw.Draw(image)
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            cx, cy = det.center
            draw.rectangle((x1, y1, x2, y2), outline=(0, 255, 0), width=2)
            draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(255, 0, 0))
        return np.array(image)

    def _adjust_range(
        self,
        low: Tuple[int, int, int],
        high: Tuple[int, int, int],
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Adjust S/V tolerance based on user sensitivity."""
        flexibility = int((1.0 - self.sensitivity) * 60)
        low_a = np.array((low[0], max(0, low[1] - flexibility), max(0, low[2] - flexibility)))
        high_a = np.array((high[0], min(255, high[1] + flexibility), min(255, high[2] + flexibility)))
        return low_a, high_a

    def _connected_components(self, mask: np.ndarray) -> List[Detection]:
        visited = np.zeros(mask.shape, dtype=bool)
        detections: List[Detection] = []
        height, width = mask.shape

        for y in range(height):
            for x in range(width):
                if not mask[y, x] or visited[y, x]:
                    continue

                queue = deque([(x, y)])
                visited[y, x] = True
                count = 0
                min_x = max_x = x
                min_y = max_y = y

                while queue:
                    cx, cy = queue.popleft()
                    count += 1
                    min_x = min(min_x, cx)
                    max_x = max(max_x, cx)
                    min_y = min(min_y, cy)
                    max_y = max(max_y, cy)

                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < width and 0 <= ny < height and mask[ny, nx] and not visited[ny, nx]:
                            visited[ny, nx] = True
                            queue.append((nx, ny))

                if count >= self.min_pixels:
                    center = ((min_x + max_x) // 2, (min_y + max_y) // 2)
                    detections.append(Detection(center=center, bbox=(min_x, min_y, max_x, max_y), pixels=count))

        return detections

    @staticmethod
    def _rgb_to_hsv_255(rgb: np.ndarray) -> np.ndarray:
        """Convert RGB uint8 image to HSV uint8-like scale [0-255]."""
        rgb_f = rgb.astype(np.float32) / 255.0
        r, g, b = rgb_f[..., 0], rgb_f[..., 1], rgb_f[..., 2]

        cmax = np.max(rgb_f, axis=2)
        cmin = np.min(rgb_f, axis=2)
        delta = cmax - cmin

        h = np.zeros_like(cmax)
        nonzero = delta != 0

        mask = (cmax == r) & nonzero
        h[mask] = ((g[mask] - b[mask]) / delta[mask]) % 6

        mask = (cmax == g) & nonzero
        h[mask] = ((b[mask] - r[mask]) / delta[mask]) + 2

        mask = (cmax == b) & nonzero
        h[mask] = ((r[mask] - g[mask]) / delta[mask]) + 4

        h = (h * 60.0) / 360.0
        s = np.zeros_like(cmax)
        non_black = cmax != 0
        s[non_black] = delta[non_black] / cmax[non_black]
        v = cmax

        hsv = np.stack((h * 255.0, s * 255.0, v * 255.0), axis=2)
        return hsv.astype(np.uint8)
