from __future__ import annotations

from typing import Dict, List, Tuple, Type

import numpy as np


class BaseKeypoints:
    """Store keypoints data.

    Attributes:
        labels (List[str]): List with the name of the keypoints.
        keypoints (np.ndarray): Array of shape (K, 3), where K is the number of
            keypoints and the last dimension corresponds to (x, y, confidence),
            where x and y are the relative image coordinates.
        confidence_threshold (float): Minimum keypoints confidence.

    Overloaded operators:
        __len__
        __eq__
        __str__
        __repr__
        __iter__
    """

    labels: List[str] = []

    def __init__(self, keypoints: np.ndarray,
                 confidence_threshold: float = 0.05):
        """
        Args:
            keypoints (np.ndarray): Array of shape (K, 3), where K is the
                number of keypoints and the last dimension corresponds to
                (x, y, confidence), where x and y are the relative image
                coordinates.
            confidence_threshold (float, optional): Keypoints confidence
                threshold to determine if a keypoint is visible or not.
                Defaults to 0.05.
        """
        self.keypoints = keypoints
        self.confidence_threshold = confidence_threshold

    @staticmethod
    def from_named_keypoints(
        named_keypoints: Dict[str, Tuple[float, float, float]],
        **kwargs
    ) -> BaseKeypoints:
        """Create a Keypoints object from a dict of named keypoints.

        Args:
            named_keypoints (Dict[str, Tuple[float, float, float]]): A dict
                with the keypoints by its name. Keypoints must come in the form
                of (x, y, confidence), where x and y are the relative image
                coordinates.

        Returns:
            BaseKeypoints
        """
        l = int(max(named_keypoints.keys(), key=lambda x: int(x)))
        kp = np.zeros((l, 3), dtype=float)
        for n, k in named_keypoints.items():
            kp[int(n)] = k
        return BaseKeypoints(kp, **kwargs)

    @classmethod
    def from_absolute_keypoints(cls, keypoints: np.ndarray, image_width: int,
                                image_height: int, **kwargs
                                ) -> Type[BaseKeypoints]:
        rel_kp = keypoints.copy()
        rel_kp[:, 0] /= image_width
        rel_kp[:, 1] /= image_height
        return cls(rel_kp, **kwargs)

    @property
    def named_keypoints(self) -> Dict[str, Tuple[float, float, float]]:
        """Return a dict with the keypoints by its name.
        """
        return {
            str(i): list(map(float, kp))
            for i, kp in enumerate(self.keypoints)
        }

    @property
    def visible_keypoints(self) -> Dict[str, Tuple[float, float, float]]:
        """Return a dict with only the visible keypoints. Visible keypoints
        are those with a confidence greater or equal than
        ``confidence_threshold``.

        Returns:
            Dict[str, Tuple[float, float, float]]: Dict of visible keypoints
                by its name.
        """
        return {
            name: kp
            for name, kp in self.named_keypoints.items()
            if kp[2] >= self.confidence_threshold
        }

    def __len__(self) -> int:
        """Number of visible keypoints.
        """
        return len(self.visible_keypoints)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} ({len(self)})"

    def __repr__(self) -> str:
        return f"BaseKeypoints({repr(self.keypoints)})"

    def serialize(self) -> dict:
        """Serialize to a basic Python datatype.

        Returns:
            dict
        """
        return self.visible_keypoints

    @classmethod
    def deserialize(cls, keypoints_dict: dict) -> BaseKeypoints:
        """Deserialize value.

        Args:
            keypoints_dict (dict)

        Returns:
            BaseKeypoints
        """
        return cls.from_named_keypoints(keypoints_dict)

    def __eq__(self, other: BaseKeypoints) -> bool:
        if not isinstance(other, BaseKeypoints):
            return False
        return np.array_equal(self.keypoints, other.keypoints) and \
            self.confidence_threshold == other.confidence_threshold

    # Pydantic methods
    def __iter__(self):
        d = self.serialize()
        yield from d.items()

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, BaseKeypoints):
            return v
        try:
            return cls.deserialize(v)
        except:
            raise TypeError(f"Error parsing {v} ({type(v)}) to {cls}")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            example=cls(np.ones((17, 3))).serialize()
        )


class COCOKeypoints(BaseKeypoints):
    """Store keypoints data of a person with the coco format (17 keypoints).

    Attributes:
        labels (List[str]): List with the name of the keypoints.
        keypoints (np.ndarray): Array of shape (K, 3), where K is the number of
            keypoints (17) and the last dimension corresponds to
            (x, y, confidence), where x and y are the relative image
            coordinates.
        confidence_threshold (float): Minimum keypoints confidence.

    Properties (read-only):
        named_keypoints (Dict[str, Tuple[float, float, float]]): A dict of
            keypoints by their names.
        visible_keypoints (Dict[str, Tuple[float, float, float]]) A dict with
            the visible keypoints by their names
            (those with confidence >= confidence_threshold).

    Methods:
        serialize() -> dict

    Static methods:
        from_named_keypoints(named_keypoints, **kwargs) -> COCOKeypoints
        from_absolute_keypoints(keypoints, image_width, image_height, **kwargs) -> COCOKeypoints
        deserialize(keypoints_dict) -> BaseKeypoints

    Overloaded operators:
        __len__
        __eq__
        __str__
        __iter__
    """

    labels = [
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

    @property
    def named_keypoints(self) -> Dict[str, Tuple[float, float, float]]:
        """Return a dict with the keypoints by its name.
        """
        assert len(self.keypoints) == len(self.labels), \
            (len(self.keypoints), len(self.labels))

        return {
            name: list(map(float, kp))
            for kp, name in zip(self.keypoints, self.labels)
        }

    @staticmethod
    def from_named_keypoints(
        named_keypoints: Dict[str, Tuple[float, float, float]],
        **kwargs
    ) -> COCOKeypoints:
        """Create a Keypoints object from a dict of named keypoints.

        Args:
            named_keypoints (Dict[str, Tuple[float, float, float]]): A dict
                with the keypoints by its name. Keypoints must come in the form
                of (x, y, confidence), where x and y are the relative image
                coordinates.

        Returns:
            COCOKeypoints
        """
        label_map = {n: i for i, n in enumerate(COCOKeypoints.labels)}
        kp = np.zeros((len(label_map), 3), dtype=float)
        for n, k in named_keypoints.items():
            kp[label_map[n]] = k
        return COCOKeypoints(kp, **kwargs)


def keypoints_dict_to_absolute(
        keypoints_dict: Dict[str, Tuple[float, float, float]],
        image_width: int, image_height: int
) -> Dict[str, Tuple[float, float, float]]:
    return {
        name: (
            min(round(kp[0] * image_width), image_width-1),
            min(round(kp[1] * image_height), image_height-1),
            kp[2]
        )
        for name, kp in keypoints_dict.items()
    }


def keypoints_to_absolute(
        keypoints: np.ndarray, image_width: int, image_height: int
) -> np.ndarray:
    abs_kp = keypoints.copy()
    abs_kp[:0] = min(round(abs_kp[:0] * image_width), image_width-1)
    abs_kp[:1] = min(round(abs_kp[:1] * image_height), image_height-1)
    return abs_kp
