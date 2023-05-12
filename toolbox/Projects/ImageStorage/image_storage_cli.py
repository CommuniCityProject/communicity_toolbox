from typing import List, Union

import requests

from toolbox.Structures import Image
from toolbox.utils.utils import urljoin


class ImageStorageCli:

    def __init__(self, host: str, port: int, url_path: str = ""):
        """Create the image storage client.

        Args:
            host (str): Host address of the image storage server.
            port (int): Port of the image storage server.
            url_path (str, optional): URL path of the image storage server. 
                Defaults to "".
        """
        self.host = host
        self.port = port
        self.url_path = url_path
        self.url = urljoin(f"http://{self.host}:{self.port}", self.url_path)

    def upload_bytes(
        self,
        image_bytes: bytes,
        name: str,
        file_type: str,
        source: str = "",
        purpose: str = "",
        raise_on_error: bool = True
    ) -> Union[str, None]:
        """Upload an image as bytes to the image storage.

        Args:
            image_bytes (bytes): The image bytes.
            name (str): The filename of the image.
            file_type (str): The MIME type of the image.
            source (str, optional): Optional source os the image.
                Defaults to "".
            purpose (str, optional): Optional purpose of the image.
                Defaults to "".
            raise_on_error (bool, optional): Raises an exception if the request
                fails. Defaults to True.

        Raises:
            HTTPError: If the request fails and ``raise_on_error`` is True.

        Returns:
            Union[str, None]: The ID of the uploaded image if the request was
                successful, else None.
        """
        files = {"file": (name, image_bytes, file_type)}
        data = {
            "source": source,
            "purpose": purpose
        }
        headers = {"accept": "application/json"}
        r = requests.post(self.url, headers=headers, data=data, files=files)
        if not r.ok:
            if raise_on_error:
                r.raise_for_status()
            return None
        return r.json()

    def download(
        self,
        image_id: str,
        raise_on_error: bool = True
    ) -> Union[Image, None]:
        """Download an image from the image storage.

        Args:
            image_id (str): The ID of the image to download.
            raise_on_error (bool, optional): Raises an exception if the request
                fails. Defaults to True.

        Raises:
            Exception if the request fails and ``raise_on_error`` is True.

        Returns:
            Union[Image, None]: The downloaded image if the request was
                successful, else None.
        """
        url = urljoin(self.url, image_id)
        try:
            img = Image.from_url(url)
            img.id = image_id
            return img
        except Exception as e:
            if raise_on_error:
                raise e
            return None

    def visualize(
        self,
        entity_ids: List[str],
        visualization_params: dict = {},
        raise_on_error: bool = True
    ) -> Union[str, None]:
        """Create a visualization of the given entity ids.

        Args:
            entity_ids (List[str]): List of entity ids to visualize.
            visualization_params (dict, optional): Visualization parameters.
                Defaults to {}.
            raise_on_error (bool, optional): Raise an ``HTTPError`` exception
                if the request fails. Defaults to True.

        Raises:
            HTTPError: If the request fails and ``raise_on_error`` is True.

        Returns:
            Union[str, None]: ID of the generated image if the request was
                successful, else None.
        """
        url = urljoin(self.url, "visualize")
        content = {
            "entity_ids": entity_ids,
            "params": visualization_params
        }
        r = requests.post(url, json=content)
        if not r.ok:
            if raise_on_error:
                r.raise_for_status()
            return None
        return r.json()
