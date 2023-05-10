import argparse
from pathlib import Path
from typing import Type

import streamlit as st
from project_templates import BaseTemplate, project_templates

from toolbox.utils.config_utils import parse_config
from toolbox.utils.utils import get_logger

logger = get_logger("toolbox.FrontEnd")


def get_project_templates(project_params: dict) -> Type[BaseTemplate]:
    """Get a project template object from the project parameters.

    Args:
        project_params (dict): A project parameters dict.

    Returns:
        Type[BaseTemplate]: A project template object.
    """
    template_cls = project_templates[project_params["template"]]
    template = template_cls(**project_params)
    return template


def app(config: dict):
    """Run the main UI application.

    Args:
        config (dict): A configuration dict.
    """
    st.set_page_config(layout="wide")

    # Parse the Projects APIs configuration
    templates = [get_project_templates(p) for p in config["projects"]]
    
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
    logger.setLevel(args.log_level)
    config = parse_config(args.config)
    app(config)


if __name__ == "__main__":
    main()
