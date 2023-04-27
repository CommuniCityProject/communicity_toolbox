from typing import Dict, List
import cv2
import numpy as np
import pycocotools.mask as mask_utils

from toolbox.utils import BoundingBox



KP_LABELS = [
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle"
]


def parse_keypoints(keypoints: np.ndarray) -> Dict[str, tuple]:
    """Parse a keypoints array to a dictionary.

    Args:
        keypoints (np.ndarray): Array of keypoints of shape (17,3), where each
          point is (x, y, keypoint-confidence).

    Returns:
        Dict[str, tuple]: Dict of pairs of body-part-name and keypoint tuple
          (x, y, keypoint-confidence).
    """
    return {
        name: (int(kp[0]), int(kp[1]), float(kp[2]))
        for kp, name in zip(keypoints, KP_LABELS)
    }
    