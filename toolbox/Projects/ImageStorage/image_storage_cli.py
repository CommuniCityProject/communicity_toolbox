import requests

from toolbox.Structures import Image


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
        self.url_path = "/" + url_path \
            if not url_path.startswith("/") else url_path
        self.url = f"http://{self.host}:{self.port}{self.url_path}"
    
    def upload_bytes(self, image_bytes: bytes, name: str, file_type: str,
                      source: str = "", purpose: str = "") -> str:
        files = {"file": (name, image_bytes, file_type)}
        data = {
            "source": "test_source",
            "purpose": "test_purpose"
        }
        headers = {"accept": "application/json"}
        r = requests.post(self.url, headers=headers, data=data, files=files)
        if not r.ok:
            raise ValueError(r.text)
        return r.json()

    def download(self, image_id: str) -> Image:
        img = Image.from_url(self.url + image_id)
        img.id = image_id
        return img
