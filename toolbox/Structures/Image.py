from __future__ import annotations

import urllib.request
from pathlib import Path
from typing import Dict, Optional, Union

import cv2
import numpy as np

from toolbox.utils.utils import is_url


class Image:
    """Structure to store an image. Allow to load an image from a local file
    or an URL.

    Attributes:
        path (Union[str, Path]): Path or URL to an image.
        id (str): Id of a ngsi-ld image entity.

    Overloaded operators:
        __str__
        __eq__
        __repr__
        __iter__
    """

    def __init__(self, path: Union[str, Path] = "",
                 image: Optional[np.ndarray] = None,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 id: str = ""):
        """Create an Image object.

        Args:
            path (Union[str, Path], optional): Path or URL to an image.
                Defaults to "".
            image (Optional[np.ndarray], optional): A np.ndarray image.
                Defaults to None.
            width (Optional[int], optional): Width of the image. Automatically
                obtained from the image if supplied. Defaults to None.
            height (Optional[int], optional): Height of the image.
                Automatically obtained from the image if supplied.
                Defaults to None.
            id (str, optional): Id of an ngsi-ld image entity.
                Defaults to "".
        """
        self.id = id
        if image is not None:
            self._height, self._width = image.shape[:2]
        else:
            self._width = width
            self._height = height
        self._image = image
        self.path = self._parse_path(path)

    @property
    def image(self) -> np.ndarray:
        """Return the image as a numpy array, load the image if it's necessary.
        """
        if self._image is None:
            self._load_image()
        return self._image

    @property
    def height(self) -> int:
        """Return the height of the image, load the image if it's necessary.
        """
        if self._height is None:
            self._load_image()
        return self._height

    @property
    def width(self) -> int:
        """Return the width of the image, load the image if it's necessary.
        """
        if self._width is None:
            self._load_image()
        return self._width

    def load_image(self):
        """Manually load the image into memory.
        """
        if self._image is None:
            self._load_image()

    def save_image(self, path: Optional[Union[str, Path]] = None):
        """Save the image to a file.

        Args:
            path (Optional[Union[str, Path]]): Optional output file path.
                If None, the ``self.path`` will be used
        """
        path = self.path if path is None else path
        path = Path(path)
        try:        
            cv2.imwrite(str(path), self.image)
        except Exception as e:
            raise OSError(f"Can not write image to {path}") from e

    def _parse_path(self, path: Union[str, Path]) -> Union[str, Path]:
        """Return a Path object if the path is a local file or a string if
        the path is a URL.
        """
        if isinstance(path, Path):
            return path
        if not is_url(path):
            return Path(path)
        return path

    def _load_image(self):
        """Load an image form disk or an URL.

        Raises:
            FileNotFoundError
            IsADirectoryError
            ValueError
        """
        if isinstance(self.path, Path):
            self._load_path(self.path)
        else:
            self._load_url(self.path)

    def _load_path(self, path: Path) -> None:
        """Load the image from a local path.

        Args:
            path (Path): Path to an image.

        Returns:
            None

        Raises:
            FileNotFoundError
            IsADirectoryError
            ValueError
        """
        if not path.exists():
            raise FileNotFoundError(path)
        if path.is_dir():
            raise IsADirectoryError(path)
        self._image = cv2.imread(str(path))
        if self._image is None:
            raise ValueError(f"Error reading image from {path}")
        self._height, self._width = self._image.shape[:2]

    def _load_url(self, url: str) -> None:
        """Load the image from an URL.

        Args:
            url (str): URL of an image.

        Returns:
            None

        Raises:
            ValueError
        """
        try:
            with urllib.request.urlopen(url) as req:
                arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
                self._image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                if self._image is None:
                    raise ValueError(f"Error reading image from {url}")
                self._height, self._width = self._image.shape[:2]
        except urllib.error.HTTPError as e:
            raise ValueError(f"Error reading image from {url}") from e

    @staticmethod
    def from_url(url: str) -> Image:
        """Create an Image object from an URL.

        Args:
            url (str): URL to an image.

        Returns:
            Image.
        """
        image = Image("")
        image.path = url
        image._load_url(url)
        return image

    @staticmethod
    def from_path(path: Path) -> Image:
        """Create an Image object from a Path.

        Args:
            path (Path): Path to an image file.

        Returns:
            Image.
        """
        image = Image("")
        image.path = Path(path)
        image._load_path(image.path)
        return image

    def __str__(self):
        return f"Image: {self.path} ({self.width} X {self.height})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path},"\
            f"width={self.width},height={self.height},id=" \
            f"'{self.id}'"

    def serialize(self) -> Dict[str, int]:
        """Serialize to a basic Python datatype.

        Returns:
            Dict[str, int]
        """
        return {
            "path": str(self.path),
            "width": self.width,
            "height": self.height,
            "id": self.id
        }

    @staticmethod
    def deserialize(value: Dict[str, int]) -> Image:
        """Deserialize value.

        Args:
            value (Dict[str, int])

        Returns:
            Image
        """
        return Image(
            path=value["path"],
            width=value["width"],
            height=value["height"],
            id=value["id"]
        )

    def __eq__(self, other: Image) -> bool:
        if not isinstance(other, Image):
            return False
        if self._image is not None and other._image is not None:
            if not np.array_equal(self._image, other._image):
                return False
        return self.serialize() == other.serialize()

    # Pydantic methods
    def __iter__(self):
        d = self.serialize()
        yield from d.items()

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, Image):
            return v
        try:
            return Image.deserialize(v)
        except:
            raise TypeError(f"Error parsing {v} ({type(v)}) to {cls}")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(example=Image(width=1920, height=1080).serialize())
