import json
import tempfile
import unittest
from pathlib import Path

from config import ConfigError, ConfigManager


class ConfigManagerTests(unittest.TestCase):
    def test_creates_default_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.json"
            manager = ConfigManager(str(config_path))
            data = manager.load()
            self.assertTrue(config_path.exists())
            self.assertIn("capture", data)

    def test_rejects_invalid_capture_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "capture": {
                            "region": {"left": 0, "top": 0, "width": 0, "height": 720},
                            "fps_limit": 30,
                        }
                    }
                ),
                encoding="utf-8",
            )
            manager = ConfigManager(str(config_path))
            with self.assertRaises(ConfigError):
                manager.load()


if __name__ == "__main__":
    unittest.main()
