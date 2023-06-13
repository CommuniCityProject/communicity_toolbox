from __future__ import annotations

from typing import Dict, Optional, Tuple, Union

import numpy as np


class BoundingBox:
    """Structure to store a bounding box.

    Attributes:
        xmin (float): Minimum relative x coordinate.
        ymin (float): Minimum relative y coordinate.
        xmax (float): Maximum relative x coordinate.
        ymax (float): Maximum relative y coordinate.

    Overloaded operators:
        __repr__
        __eq__
        __bool__
        __iter__
    """

    def __init__(self, xmin: float, ymin: float, xmax: float, ymax: float):
        """Create a bounding box object with the relative coordinates to the
        image size of the top-left and bottom-right corners.

        Args:
            xmin (float): Minimum relative x coordinate.
            ymin (float): Minimum relative y coordinate.
            xmax (float): Maximum relative x coordinate.
            ymax (float): Maximum relative y coordinate.
        """
        self.xmin = max(min(float(xmin), 1), 0)
        self.ymin = max(min(float(ymin), 1), 0)
        self.xmax = max(min(float(xmax), 1), 0)
        self.ymax = max(min(float(ymax), 1), 0)

    def _to_absolute(self, rel_value: float, dim: int) -> int:
        """Convert a relative value to absolute.

        Args:
            rel_value (float): Relative value to convert.
            dim (int): Absolute dimension.

        Returns:
            int: The absolute value.
        """
        return min(round(rel_value * dim), dim)

    def get_width(self, absolute: bool = False,
                  image_width: Optional[int] = None) -> Union[float, int]:
        """Get the width of the bounding box.

        Args:
            absolute (bool, optional): Return the absolute value,
                otherwise relative to the image. Defaults to False.
            image_width (Optional[int], optional): Image width.
                Defaults to None.

        Returns:
            Union[float, int]: The width of the bounding box.
        """
        assert not absolute or image_width is not None, (absolute, image_width)
        width = self.xmax - self.xmin
        if absolute:
            width = self._to_absolute(width, image_width)
        return width

    def get_height(self, absolute: bool = False,
                   image_height: Optional[int] = None) -> Union[float, int]:
        """Get the height of the bounding box.

        Args:
            absolute (bool, optional): Return the absolute value,
                otherwise relative to the image. Defaults to False.
            image_height (Optional[int], optional): Image height.
                Defaults to None.

        Returns:
            Union[float, int]: The height of the bounding box.
        """
        assert not absolute or image_height is not None, (
            absolute, image_height)
        height = self.ymax - self.ymin
        if absolute:
            height = self._to_absolute(height, image_height)
        return height

    def get_center_x(self, absolute: bool = False,
                     image_width: Optional[int] = None) -> Union[float, int]:
        """Get the center x coordinate of the bounding box.

        Args:
            absolute (bool, optional): Return the absolute coordinate,
                otherwise relative to the image. Defaults to False.
            image_width (Optional[int], optional): Image width.
                Defaults to None.

        Returns:
            Union[float, int]: The center x coordinate.
        """
        cx = (self.xmax + self.xmin) / 2
        if absolute:
            cx = self._to_absolute(cx, image_width)
        return cx

    def get_center_y(self, absolute: bool = False,
                     image_height: Optional[int] = None) -> Union[float, int]:
        """Get the center y coordinate of the bounding box.

        Args:
            absolute (bool, optional): Return the absolute coordinate,
                otherwise relative to the image. Defaults to False.
            image_height (Optional[int], optional): Image height.
                Defaults to None.

        Returns:
            Union[float, int]: The center y coordinate.
        """
        cy = (self.ymax + self.ymin) / 2
        if absolute:
            cy = self._to_absolute(cy, image_height)
        return cy

    def get_area(self, absolute: bool = False,
                 image_width: Optional[int] = None,
                 image_height: Optional[int] = None) -> Union[float, int]:
        """Get the area of the bounding box.

        Args:
            absolute (bool, optional): Return the absolute value,
                otherwise relative to the image. Defaults to False.
            image_width (Optional[int], optional): Image width.
                Defaults to None.
            image_height (Optional[int], optional): Image height.
                Defaults to None.

        Returns:
            float: The area of the bounding box.
        """
        assert (not absolute) or \
            (image_height is not None and image_width is not None), \
            (absolute, image_height, image_width)
        return (
            self.get_width(absolute, image_width) *
            self.get_height(absolute, image_height)
        )

    def get_xyxy(self, absolute: bool = False,
                 image_width: Optional[int] = None,
                 image_height: Optional[int] = None) -> np.ndarray:
        """Get the maximum and minimum bounding box coordinates as a numpy
        array.

        Args:
            absolute (bool, optional): Return the absolute value,
                otherwise relative to the image. Defaults to False.
            image_width (Optional[int], optional): Image width.
                Defaults to None.
            image_height (Optional[int], optional): Image height.
                Defaults to None.

        Returns:
            np.ndarray: [minimum x, minimum y, maximum x, maximum y].
        """
        assert (not absolute) or \
            (image_height is not None and image_width is not None), \
            (absolute, image_height, image_width)
        if absolute:
            return np.array([
                self._to_absolute(self.xmin, image_width),
                self._to_absolute(self.ymin, image_height),
                self._to_absolute(self.xmax, image_width),
                self._to_absolute(self.ymax, image_height)
            ], int)
        return np.array([self.xmin, self.ymin, self.xmax, self.ymax])

    def get_xywh(self, absolute: bool = False,
                 image_width: Optional[int] = None,
                 image_height: Optional[int] = None) -> np.ndarray:
        """Get the center coordinates and the box width and height as a
        numpy array.

        Args:
            absolute (bool, optional): Return the absolute value,
                otherwise relative to the image. Defaults to False.
            image_width (Optional[int], optional): Image width.
                Defaults to None.
            image_height (Optional[int], optional): Image height.
                Defaults to None.

        Returns:
            np.ndarray: [center x, center y, box width, box height].
        """
        return np.array([
            self.get_center_x(absolute, image_width),
            self.get_center_y(absolute, image_height),
            self.get_width(absolute, image_width),
            self.get_height(absolute, image_height)
        ])

    @classmethod
    def from_absolute(cls, xmin: int, ymin: int, xmax: int, ymax: int,
                      image_width: int, image_height: int) -> BoundingBox:
        """Create a bounding box object from the absolute image coordinates of
        the top-left and bottom-right corners.

        Args:
            xmin (int): Minimum x coordinate.
            ymin (int): Minimum y coordinate.
            xmax (int): Maximum x coordinate.
            ymax (int): Maximum y coordinate.
            image_width (int): Image width.
            image_height (int): Image height.

        Returns:
            BoundingBox: A BoundingBox object.
        """
        return cls(
            xmin/image_width,
            ymin/image_height,
            xmax/image_width,
            ymax/image_height
        )

    @ staticmethod
    def from_xywh(x: Union[float, int], y: Union[float, int],
                  w: Union[float, int], h: Union[float, int],
                  absolute: bool = False, image_width: Optional[int] = None,
                  image_height: Optional[int] = None) -> BoundingBox:
        """Create a bounding box object from the center coordinates and the
        width and height of a box.

        Args:
            x (float): Center x coordinate.
            y (float): Center y coordinate.
            w (float): Width of the box.
            h (float): Height of the box.
            absolute (bool, optional): If the coordinates passed are relative.
                Defaults to False.
            image_width (Optional[int], optional): Image width used when
                ``absolute`` is True. Defaults to None.
            image_height (Optional[int], optional):  Image height used when
                ``absolute`` is True. Defaults to None.

        Returns:
            BoundingBox: A BoundingBox object.
        """
        assert (not absolute) or \
            (image_height is not None and image_width is not None), \
            (absolute, image_height, image_width)
        if absolute:
            x /= image_width
            y /= image_height
            w /= image_width
            h /= image_height
        w2 = w/2
        h2 = h/2
        xmin = max(x - w2, 0)
        ymin = max(y - h2, 0)
        xmax = min(x + w2, 1)
        ymax = min(y + h2, 1)
        return BoundingBox(xmin, ymin, xmax, ymax)

    def crop_image(self, image: np.ndarray) -> np.ndarray:
        """Crop an image with the bounding box.

        Args:
            image (np.ndarray): Numpy image of shape (h, w, c) or (h, w).

        Returns:
            np.ndarray: A cropped copy of the image with the region inside the
                bounding box.
        """
        xmin, ymin, xmax, ymax = self.get_xyxy(
            True, image.shape[1], image.shape[0])
        return image.copy()[ymin:ymax, xmin:xmax]

    def scale(self, factor: Union[Tuple[float, float], float]) -> BoundingBox:
        """Scale the bounding box from the center by a factor.

        Args:
            factor (Union[Tuple[float, float], float]): A value by which both
                width and height will be scaled or a tuple with the
                width-factor and the height-factor.

        Returns:
            BoundingBox: A new scaled BoundingBox object.
        """
        if isinstance(factor, (float, int)):
            factor = [factor, factor]
        fx, fy = factor

        _mfx2 = (1-fx)/2
        _pfx2 = (1+fx)/2
        _mfy2 = (1-fy)/2
        _pfy2 = (1+fy)/2

        xmin = (self.xmax * _mfx2) + (self.xmin * _pfx2)
        xmax = (self.xmax * _pfx2) + (self.xmin * _mfx2)
        ymin = (self.ymax * _mfy2) + (self.ymin * _pfy2)
        ymax = (self.ymax * _pfy2) + (self.ymin * _mfy2)

        return BoundingBox(xmin, ymin, xmax, ymax)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.xmin:.3f},{self.ymin:.3f},{self.xmax:.3f},{self.ymax:.3f})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.xmin},{self.ymin},{self.xmax},{self.ymax})"

    def is_empty(self) -> bool:
        """Return True if height or width is 0.
        """
        if self.get_width() <= 0:
            return True
        if self.get_height() <= 0:
            return True
        return False

    def __bool__(self):
        return not self.is_empty()

    def __eq__(self, other: BoundingBox) -> bool:
        if not isinstance(other, BoundingBox):
            return False
        return self.xmin == other.xmin and \
            self.ymin == other.ymin and \
            self.xmax == other.xmax and \
            self.ymax == other.ymax

    def serialize(self) -> Dict[str, float]:
        """Serialize to a basic Python datatype.

        Returns:
            Dict[str, float]
        """
        return {
            "xmin": self.xmin,
            "ymin": self.ymin,
            "xmax": self.xmax,
            "ymax": self.ymax,
        }

    @staticmethod
    def deserialize(value: Dict[str, float]) -> BoundingBox:
        """Deserialize value.

        Args:
            value (Dict[str, float])

        Returns:
            BoundingBox
        """
        return BoundingBox(
            xmin=value["xmin"],
            ymin=value["ymin"],
            xmax=value["xmax"],
            ymax=value["ymax"],
        )

    # Pydantic methods
    def __iter__(self):
        d = self.serialize()
        yield from d.items()

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, BoundingBox):
            return v
        try:
            return BoundingBox.deserialize(v)
        except:
            raise TypeError(f"Error parsing {v} ({type(v)}) to {cls}")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(example=BoundingBox(0, 0, 0, 0).serialize())
