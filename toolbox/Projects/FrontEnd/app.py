import argparse
import logging
from pathlib import Path
from typing import List, Tuple, Type

import streamlit as st
from project_templates import BaseTemplate, project_templates

from toolbox.Context import ContextCli
from toolbox.Projects.ImageStorage import ImageStorageCli
from toolbox.utils.config_utils import parse_config
from toolbox.utils.utils import get_logger

logger = get_logger("toolbox.FrontEnd")


def get_project_templates(
    project_params: dict,
    context_cli: ContextCli,
    image_storage_cli: ImageStorageCli
) -> Type[BaseTemplate]:
    """Get a project template object from the project parameters.

    Args:
        project_params (dict): A project parameters dict.
        context_cli (ContextCli): A context client.
        image_storage_cli (ImageStorageCli): An image storage client.

    Returns:
        Type[BaseTemplate]: A project template object.
    """
    logger.info(f"Creating project template ({project_params})")
    template_cls = project_templates[project_params["template"]]
    template = template_cls(
        **project_params,
        context_cli=context_cli,
        image_storage_cli=image_storage_cli
    )
    return template


@st.cache_resource
def init(config: dict, log_level: str = "INFO"
         ) -> Tuple[List[Type[BaseTemplate]], ImageStorageCli]:
    """Initialize the UI components.

    Args:
        config (dict): A configuration dict.
        log_level (str, optional): The logging level. Defaults to "INFO".

    Returns:
        Tuple[List[Type[BaseTemplate]], ImageStorageCli]: A tuple containing
            the project templates and the image storage client.
    """
    logging.getLogger("toolbox").setLevel(log_level)
    config = parse_config(config)

    context_cli = ContextCli(**config["context_broker"])
    image_storage_cli = ImageStorageCli(**config["image_storage"])

    # Parse the Projects APIs configuration
    templates = [
        get_project_templates(p, context_cli, image_storage_cli)
        for p in config["projects"]
    ]

    return templates, image_storage_cli


@st.cache_resource
def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--config",
        help="Path to the configuration yaml (default: 'config.yaml')",
        type=Path,
        default="config.yaml"
    )
    ap.add_argument(
        "--log-level",
        help="Log level",
        choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
        default="INFO"
    )
    args = ap.parse_args()
    return args


def app(templates: List[Type[BaseTemplate]],
        image_storage_cli: ImageStorageCli):
    """Run the main UI application.

    Args:
        templates (List[Type[BaseTemplate]]): A list of project templates.
        image_storage_cli (ImageStorageCli): An image storage client.
    """
    # Set the navigation left sidebar
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio(
        "Projects",
        list(range(len(templates))),
        format_func=lambda i: templates[i].name
    )

    # Call each project template
    templates[selection]()


def main():
    st.set_page_config(layout="wide")
    args = parse_args()
    templates, image_storage_cli = init(args.config, args.log_level)
    app(templates, image_storage_cli)


if __name__ == "__main__":
    main()
