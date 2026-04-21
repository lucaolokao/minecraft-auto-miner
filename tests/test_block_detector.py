import unittest

import numpy as np

from block_detector import BlockDetector


class BlockDetectorTests(unittest.TestCase):
    def test_detects_single_diamond_cluster(self) -> None:
        frame = np.zeros((120, 120, 3), dtype=np.uint8)
        frame[40:70, 50:80] = [0, 240, 255]  # cyan-like diamond tone

        detector = BlockDetector(sensitivity=0.8, min_pixels=50)
        detections = detector.detect_blocks(frame, "diamond")

        self.assertEqual(len(detections), 1)
        center_x, center_y = detections[0].center
        self.assertTrue(60 <= center_x <= 70)
        self.assertTrue(50 <= center_y <= 60)


if __name__ == "__main__":
    unittest.main()
