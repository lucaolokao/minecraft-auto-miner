"""Entry point for the Minecraft Auto-Miner bot."""

from __future__ import annotations

import argparse
import signal
import threading
import time
from dataclasses import dataclass
from typing import List

from block_detector import BlockDetector
from config import ConfigManager
from constants import (
    STATUS_MINING,
    STATUS_PAUSED,
    STATUS_RUNNING,
    STATUS_STOPPED,
    SUPPORTED_BLOCKS,
)
from input_handler import InputHandler
from screen_capture import ScreenCapture
from utils import format_status_line, setup_logger


@dataclass
class RuntimeStats:
    """Tracks runtime counters for status output."""

    frame_counter: int = 0
    detected_counter: int = 0
    last_fps_reset: float = 0.0
    current_fps: float = 0.0


class AutoMinerBot:
    """Coordinates capture, detection and mining automation."""

    def __init__(self, config_path: str = "config.json") -> None:
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load()

        self.logger = setup_logger(
            "auto_miner",
            level=self.config["runtime"]["log_level"],
            log_file=self.config["logging"]["file"],
        )

        self.capture = ScreenCapture(
            region=self.config["capture"]["region"],
            fps_limit=self.config["capture"]["fps_limit"],
        )
        self.detector = BlockDetector(
            sensitivity=self.config["detection"]["sensitivity"],
            min_pixels=self.config["detection"]["min_pixels"],
        )
        self.input_handler = InputHandler()

        self.status = STATUS_STOPPED
        self.paused = False
        self.stop_event = threading.Event()
        self.stats = RuntimeStats(last_fps_reset=time.monotonic())

    def run(self, block_name: str) -> None:
        """Start mining loop for chosen block."""
        if block_name not in SUPPORTED_BLOCKS:
            raise ValueError(f"Unsupported block: {block_name}")
        if not self.input_handler.input_available:
            raise RuntimeError(
                "Mouse automation backend unavailable. Ensure a desktop session is active."
            )

        self._register_signal_handlers()
        self._register_hotkeys()

        self.capture.start()
        self.status = STATUS_RUNNING
        self.logger.info("Bot started for target block: %s", block_name)

        max_targets = self.config["detection"]["max_targets_per_frame"]
        idle_sleep = self.config["runtime"]["idle_sleep_seconds"]
        mine_hold = self.config["input"]["mine_hold_seconds"]
        region_left = self.config["capture"]["region"]["left"]
        region_top = self.config["capture"]["region"]["top"]

        try:
            while not self.stop_event.is_set():
                if self.paused:
                    self.status = STATUS_PAUSED
                    time.sleep(idle_sleep)
                    continue

                frame = self.capture.get_latest_frame()
                if frame is None:
                    time.sleep(idle_sleep)
                    continue

                detections = self.detector.detect_blocks(frame, block_name)
                self.stats.frame_counter += 1
                self.stats.detected_counter += len(detections)
                self._update_fps()

                if detections:
                    self.status = STATUS_MINING
                    for detection in detections[:max_targets]:
                        if self.stop_event.is_set() or self.paused:
                            break
                        screen_x = region_left + detection.center[0]
                        screen_y = region_top + detection.center[1]
                        self.input_handler.move_to(
                            (screen_x, screen_y),
                            steps=self.config["input"]["move_steps"],
                            delay=self.config["input"]["move_delay"],
                        )
                        self.input_handler.hold_mine(mine_hold)
                else:
                    self.status = STATUS_RUNNING

                print(
                    "\r" + format_status_line(self.status, block_name, len(detections), self.stats.current_fps),
                    end="",
                    flush=True,
                )
                time.sleep(idle_sleep)
        finally:
            print()
            self.shutdown()

    def pause(self) -> None:
        """Pause mining loop."""
        self.paused = True
        self.logger.info("Bot paused")

    def resume(self) -> None:
        """Resume mining loop."""
        self.paused = False
        self.logger.info("Bot resumed")

    def stop(self) -> None:
        """Stop mining loop."""
        self.stop_event.set()
        self.logger.info("Stop requested")

    def shutdown(self) -> None:
        """Gracefully stop services and release resources."""
        self.status = STATUS_STOPPED
        self.stop_event.set()
        self.capture.stop()
        self.input_handler.unregister_hotkeys()
        self.logger.info("Bot stopped gracefully")

    def _register_hotkeys(self) -> None:
        hotkeys = self.config["input"]["hotkeys"]
        self.input_handler.register_hotkeys(
            stop_key=hotkeys["stop"],
            pause_key=hotkeys["pause"],
            resume_key=hotkeys["resume"],
            on_stop=self.stop,
            on_pause=self.pause,
            on_resume=self.resume,
        )

    def _register_signal_handlers(self) -> None:
        signal.signal(signal.SIGINT, lambda *_: self.stop())
        signal.signal(signal.SIGTERM, lambda *_: self.stop())

    def _update_fps(self) -> None:
        now = time.monotonic()
        delta = now - self.stats.last_fps_reset
        if delta >= 1.0:
            self.stats.current_fps = self.stats.frame_counter / delta
            self.stats.frame_counter = 0
            self.stats.last_fps_reset = now


def choose_block() -> str:
    """Prompt user to choose a supported block."""
    print("\nAvailable blocks:")
    for index, block in enumerate(SUPPORTED_BLOCKS, start=1):
        print(f"  {index:2d}. {block}")

    while True:
        raw = input("\nType block name (or number): ").strip().lower()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(SUPPORTED_BLOCKS):
                return SUPPORTED_BLOCKS[idx]
        elif raw in SUPPORTED_BLOCKS:
            return raw
        print("Invalid selection. Try again.")


def confirm_start() -> bool:
    """Require explicit user confirmation before automation begins."""
    answer = input("Safety check: keep Minecraft focused. Start bot now? [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def parse_args() -> argparse.Namespace:
    """CLI arguments."""
    parser = argparse.ArgumentParser(description="Minecraft Auto-Miner")
    parser.add_argument("--block", choices=SUPPORTED_BLOCKS, help="Block type to mine")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    parser.add_argument("--list-blocks", action="store_true", help="List supported blocks and exit")
    return parser.parse_args()


def main() -> int:
    """Program entrypoint."""
    args = parse_args()

    if args.list_blocks:
        for block in SUPPORTED_BLOCKS:
            print(block)
        return 0

    block = args.block or choose_block()
    if not confirm_start():
        print("Cancelled.")
        return 0

    bot = AutoMinerBot(config_path=args.config)
    bot.run(block)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
