from typing import List, Union
from pathlib import Path
import mimetypes
import tempfile

import requests
import numpy as np
import cv2

from toolbox.Structures import Image
from toolbox.utils.utils import get_logger, urljoin

logger = get_logger("toolbox.ImageStorageCli")


class ImageStorageCli:
    """A class to interact with the ImageStorage API.

    Attributes:
        host (str): address of the API.
        port (int): Port of API.
        url_path (str): URL path of the API.
        url (str): The full URL of the API.
    """

    def __init__(self, host: str, port: int, url_path: str = ""):
        """Create the image storage client.

        Args:
            host (str): Address of the API.
            port (int): Port of the API.
            url_path (str, optional): URL path of the API. Defaults to "".
        """
        self.host = host
        self.port = port
        self.url_path = url_path
        self.url = urljoin(f"http://{self.host}:{self.port}", self.url_path)
        logger.info(f"Using the image storage {self.url}")

    def upload_file(
        self,
        path: Union[str, Path],
        source: str = "",
        purpose: str = "",
    ) -> str:
        """Upload an image file to the image storage.

        Args:
            path (Union[str, Path]): Path to an image file.
            source (str, optional): Optional source of the image.
                Defaults to "".
            purpose (str, optional): Optional purpose of the image.
                Defaults to "".

        Returns:
            str: The ID of the uploaded image.
        """
        path = Path(path)
        mime = mimetypes.guess_type(path)[0]
        with open(path, "rb") as f:
            data = f.read()
        return self.upload_bytes(
            image_bytes=data,
            name=path.name,
            file_type=mime,
            source=source,
            purpose=purpose
        )

    def upload_image(
        self,
        image: np.ndarray,
        file_name: str = "image.png",
        source: str = "",
        purpose: str = "",
    ) -> str:
        """Upload a numpy image to the image storage.

        Args:
            image (np.ndarray): The numpy image to upload.
            file_name (str, optional): File name of the image that will be
                created. Defaults to "image.png".
            source (str, optional): Optional source of the image.
                Defaults to "".
            purpose (str, optional): Optional purpose of the image.
                Defaults to "".

        Returns:
            str: The ID of the uploaded image.
        """
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / file_name
            cv2.imwrite(str(image_path), image)
            return self.upload_file(
                path=image_path,
                source=source,
                purpose=purpose
            )

    def upload_bytes(
        self,
        image_bytes: bytes,
        name: str,
        file_type: str,
        source: str = "",
        purpose: str = "",
    ) -> str:
        """Upload an image bytes to the image storage.

        Args:
            image_bytes (bytes): The image bytes.
            name (str): The filename of the image.
            file_type (str): The MIME type of the image.
            source (str, optional): Optional source of the image.
                Defaults to "".
            purpose (str, optional): Optional purpose of the image.
                Defaults to "".

        Raises:
            requests.exceptions.HTTPError: If the request fails.

        Returns:
            str: The ID of the uploaded image.
        """
        files = {"file": (name, image_bytes, file_type)}
        data = {
            "source": source,
            "purpose": purpose
        }
        headers = {"accept": "application/json"}
        logger.info(f"Uploading image {name} to {self.url}")
        r = requests.post(self.url, headers=headers, data=data, files=files)
        if r.ok:
            return r.json()
        logger.error(
            f"Error uploading image. Got {r.status_code} ({r.text})")
        r.raise_for_status()

    def download(self, image_id: str) -> Image:
        """Download an image from the image storage.

        Args:
            image_id (str): The ID of the image to download.

        Raises:
            Exception: If the request fails.

        Returns:
            Structures.Image.Image: The downloaded image object.
        """
        url = urljoin(self.url, image_id)
        logger.debug(f"Downloading image {url}")
        try:
            img = Image.from_url(url)
            img.id = image_id
            return img
        except Exception as e:
            logger.error(f"Error downloading image {image_id}. Got {e}")
            raise e

    def visualize(
        self,
        entity_ids: List[str],
        visualization_params: dict = {},
    ) -> str:
        """Create a visualization of the given entity IDs.

        Args:
            entity_ids (List[str]): List of entity IDs to visualize.
            visualization_params (dict, optional): Visualization parameters.
                Defaults to {}.

        Raises:
            requests.exceptions.HTTPError: If the request fails.

        Returns:
            str: ID of the generated image.
        """
        url = urljoin(self.url, "visualize")
        content = {
            "entity_ids": entity_ids,
            "params": visualization_params
        }
        logger.debug(
            f"Visualizing {entity_ids} with {visualization_params} on {url}")
        r = requests.post(url, json=content)
        if r.ok:
            return r.json()
        logger.error(
            f"Error visualizing entities. Got {r.status_code} ({r.text})")
        r.raise_for_status()
