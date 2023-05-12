from typing import Optional

import streamlit as st

from toolbox.utils.utils import get_logger, urljoin
from toolbox.Projects.ImageStorage import ImageStorageCli


class BaseTemplate:

    def __init__(self, name: str, host: str, port: int, url_path: str,
                 image_storage_cli: Optional[ImageStorageCli] = None,
                 **kwargs):
        self.logger = get_logger("toolbox.FrontEnd." + name)
        self.name = name
        self.host = host
        self.port = port
        self.url_path = url_path
        self.url = urljoin(f"http://{self.host}:{self.port}", self.url_path)
        self.image_storage_cli = image_storage_cli

    def get_api_path(self, path: str) -> str:
        if not path:
            return self.url
        return urljoin(self.url, path)

    def __call__(self):
        st.title(self.name)
