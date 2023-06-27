from typing import Optional

import streamlit as st

from toolbox.Context import ContextCli
from toolbox.Projects.ImageStorage import ImageStorageCli
from toolbox.utils.utils import get_logger, urljoin


class BaseTemplate:
    """Base class for project templates, that implements a front end for the
    different project APIs.
    """

    def __init__(self, name: str, host: str, port: int, url_path: str = "",
                 context_cli: Optional[ContextCli] = None,
                 image_storage_cli: Optional[ImageStorageCli] = None,
                 context_broker_links: bool = True, description_path: str = "",
                 public_context_broker_url: Optional[str] = None,
                 **kwargs):
        """Initialize a project template.

        Args:
            name (str): Name of the project.
            host (str): API host.
            port (int): API port.
            url_path (str, optional): API base url path. Defaults to "".
            context_cli (Optional[ContextCli], optional): Context client object.
                Defaults to None.
            image_storage_cli (Optional[ImageStorageCli], optional): Image
                storage client object. Defaults to None.
            context_broker_links (bool, optional): If True, show links to the
                Context Broker entities. Defaults to True.
            description_path (str, optional): Path to a txt file with the
                project description. Defaults to "".
            public_context_broker_url (Optional[str], optional): Context broker
                public base URL used to show the context broker links. If None
                the URL from ``context_cli`` will be used. Defaults to None.
        """
        self.logger = get_logger("toolbox.FrontEnd." + name.replace(" ", "_"))
        self.name = name
        self.host = host
        self.port = port
        self.url_path = url_path
        self.url = urljoin(f"{self.host}:{self.port}", self.url_path)
        self.context_cli = context_cli
        self.image_storage_cli = image_storage_cli
        self.context_broker_links = context_broker_links
        self.public_context_broker_url = (public_context_broker_url
            if public_context_broker_url is not None
            else self.context_cli.broker_url)

        if description_path:
            with open(description_path, "r") as f:
                self.description = f.read()
        else:
            self.description = None

    def get_api_path(self, path: str) -> str:
        if not path:
            return self.url
        return urljoin(self.url, path)

    def __call__(self):
        st.title(self.name)
