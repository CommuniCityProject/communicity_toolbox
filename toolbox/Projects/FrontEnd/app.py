import argparse
import logging
from pathlib import Path
from typing import List, Type

import streamlit as st
from streamlit_cookies_manager import CookieManager

from toolbox.Context import ContextCli
from toolbox.Projects.ImageStorage import ImageStorageCli
from toolbox.utils.config_utils import parse_config
from toolbox.utils.utils import get_logger

from project_templates import BaseTemplate, project_templates

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
def init(
    config: dict,
    log_level: str = "INFO"
) -> dict:
    """Initialize the app.

    Args:
        config (dict): A configuration dict.
        log_level (str, optional): The logging level. Defaults to "INFO".

    Returns:
        dict: A dict with the app static variables.
    """
    logging.getLogger("toolbox").setLevel(log_level)
    config = parse_config(config)

    show_agreement = config["show_agreement"]
    if show_agreement:
        with open(config["agreement_text"], "r") as f:
            agreement = f.readlines()
    else:
        agreement = None
    use_cookies = config["use_cookies"]

    # Create the context broker and image storage clients
    context_cli = ContextCli(**config["context_broker"])
    image_storage_cli = ImageStorageCli(**config["image_storage"])

    # Create the Projects templates
    templates = [
        get_project_templates(p, context_cli, image_storage_cli)
        for p in config["projects"]
    ]

    return {
        "templates": templates,
        "show_agreement": show_agreement,
        "agreement": agreement,
        "use_cookies": use_cookies
    }


@st.cache_resource
def parse_args() -> argparse.Namespace:
    """Parse the arguments of the app

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    ap = argparse.ArgumentParser(description="App parameters. Use '--' at the end of "
                                 "the streamlit command line to separate the "
                                 "streamlit arguments from the App ones.")
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


def check_agreement(
    show_agreement: bool,
    agreement: List[str],
    use_cookies: bool
) -> bool:
    """Check the status of the agreement and optionally show it.

    Args:
        show_agreement (bool): True if the agreements must be showed.
        agreement (List[str]): A list with the title and the content of the
            agreement.
        use_cookies (bool): If True, a cookie will be used to store the status
            of the agreement .

    Returns:
        bool: True if the agreement is accepted or ``show_agreement`` is False.
    """
    if st.session_state.get("accepted_agreement", False) or not show_agreement:
        return True

    if use_cookies:
        cookies = CookieManager(prefix="toolbox/")
        # Wait for the component to load and send us current cookies.
        if not cookies.ready():
            st.stop()
        # Get the agreements status from cookies
        st.session_state.accepted_agreement = cookies.get(
            "acceptedAgreement",
            False
        )
        if st.session_state.accepted_agreement:
            return True

    # Show the agreement
    st_title = st.empty()
    st_content = st.empty()
    st_button = st.empty()
    st_title.subheader(agreement[0])
    st_content.markdown(agreement[1])
    if st_button.button("Accept"):
        if use_cookies:
            cookies["acceptedAgreement"] = True
            cookies.save()
        st.session_state.accepted_agreement = True
        # Clear the agreement
        st_title.empty()
        st_content.empty()
        st_button.empty()
        return True
    return False


def app(ctx: dict):
    """Run the main UI application.

    Args:
        ctx (dict): The static variables of the app.
    """
    templates: List[Type[BaseTemplate]] = ctx["templates"]
    show_agreement: bool = ctx["show_agreement"]
    agreement: List[str] = ctx["agreement"]
    use_cookies: bool = ctx["use_cookies"]

    if check_agreement(show_agreement, agreement, use_cookies):
        # Set the navigation left sidebar
        st.sidebar.title("Navigation")
        selection = st.sidebar.radio(
            "APIs",
            list(range(len(templates))),
            format_func=lambda i: templates[i].name
        )
        # Call each project template
        templates[selection]()


def main():
    st.set_page_config(layout="wide")
    args = parse_args()
    ctx = init(args.config, args.log_level)
    app(ctx)


if __name__ == "__main__":
    main()
