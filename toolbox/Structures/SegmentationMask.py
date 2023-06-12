from __future__ import annotations

from typing import Optional

import cv2
import numpy as np
import pycocotools.mask as Mask


class SegmentationMask:
    """Store data about a single segmentation mask.

    Attributes:
        mask (np.ndarray): Binary mask of shape (H, W).

    Overloaded operators:
        __str__
        __repr__
        __eq__
        __iter__
    """

    def __init__(self, mask: Optional[np.ndarray] = None,
                 rle: Optional[dict] = None):
        """Create a SegmentationMask from a binary mask or an encoded rle.

        Args:
            mask (Optional[np.ndarray], optional): Binary mask of shape (H, W).
                Defaults to None.
            rle (Optional[dict], optional): Encoded rle mask. Defaults to None.
        """
        self.mask = Mask.decode(rle) if rle is not None else mask
        self.mask = self.mask.astype(bool)
        self.mask = np.asfortranarray(self.mask)

    @property
    def rle(self) -> dict:
        """Get the rle-encoded mask.

        Returns:
            dict: A dict with the size and rle-encoded mask.
        """
        return Mask.encode(self.mask)

    @property
    def area(self) -> float:
        return np.sum(self.mask)

    @property
    def width(self) -> int:
        return self.mask.shape[1]

    @property
    def height(self) -> int:
        return self.mask.shape[0]

    def resize(self, width: int, height: int) -> SegmentationMask:
        """Return a resized copy of the mask.

        Args:
            width (int): Target width of the mask.
            height (int): Target height of the mask.

        Returns:
            SegmentationMask: A new resized SegmentationMask object.
        """
        mask_h, mask_w = self.mask.shape[:2]
        if mask_h != height or mask_w != width:
            mask = cv2.resize(
                self.mask.astype("uint8"),
                (width, height)
            ).astype(bool)
        else:
            mask = self.mask
        return SegmentationMask(mask=mask)

    def __str__(self) -> str:
        return f"SegmentationMask ({self.width} X {self.height})"

    def __repr__(self) -> str:
        return f"SegmentationMask(rle={self.rle})"

    def serialize(self) -> dict:
        """Serialize to a basic Python datatype.

        Returns:
            dict
        """
        rle = self.rle
        rle["counts"] = rle["counts"].hex()
        return rle

    @staticmethod
    def deserialize(hex_rle: dict) -> SegmentationMask:
        """Deserialize value.

        Args:
            hex_rle (dict)

        Returns:
            SegmentationMask
        """
        hex_rle["counts"] = bytes.fromhex(hex_rle["counts"])
        return SegmentationMask(rle=hex_rle)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SegmentationMask):
            return False
        return np.array_equal(self.mask, other.mask)

    # Pydantic methods
    def __iter__(self):
        d = self.serialize()
        yield from d.items()

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, SegmentationMask):
            return v
        try:
            return SegmentationMask.deserialize(v)
        except:
            raise TypeError(f"Error parsing {v} ({type(v)}) to {cls}")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            example=SegmentationMask(mask=np.zeros((512, 512))).serialize()
        )
