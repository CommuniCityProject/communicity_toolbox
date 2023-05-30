import ast
from typing import List, Union

import streamlit as st

from toolbox.utils.utils import urljoin
from toolbox.Visualization.Defaults import Defaults


def add_visualization_params(element: st.delta_generator.DeltaGenerator):

    vis_defaults = {k: str(v) for k, v in Defaults.dict().items()}

    # Set the visualization parameters data editor
    vis_params = element.experimental_data_editor(
        {
            "Parameters": list(vis_defaults.keys()),
            "Values": list(vis_defaults.values()),
        },
        use_container_width=True
    )
    vis_params = dict(zip(
        vis_params["Parameters"],
        vis_params["Values"]
    ))

    # String to python types
    for k, v in vis_params.items():
        v_str = str(v).lower()
        if v_str in ("none", "null", ""):
            vis_params[k] = None
            continue
        if v_str in ("true", "false"):
            vis_params[k] = v_str == "true"
            continue
        if str(v)[0].isalpha():
            continue
        vis_params[k] = ast.literal_eval(v)

    return vis_params


def get_entities_broker_link(
    context_broker_url: str,
    entity_ids: Union[str, List[str]]
) -> str:
    """Get a link to a set of entities in the context broker.

    Args:
        context_broker_url (str): Base URL to the context broker.
        entity_ids (Union[str, List[str]]): A single or a list of entity IDs.

    Returns:
        str: A link to the entities in the context broker.
    """
    if isinstance(entity_ids, (list, tuple)):
        entity_ids = ",".join(entity_ids)
    return urljoin(
        context_broker_url,
        f"/ngsi-ld/v1/entities/?id={entity_ids}"
    )


def get_subscription_broker_link(
    context_broker_url: str,
    subscription_id: str
) -> str:
    return urljoin(
        context_broker_url,
        f"/ngsi-ld/v1/subscriptions/{subscription_id}"
    )


def format_st_id(ngsi_id: str) -> str:
    """Format an NGSI-LD entity ID for streamlit.

    Args:
        ngsi_id (str): An NGSI-LD entity ID.

    Returns:
        str: The formatted entity ID.
    """
    return str(ngsi_id).replace(":", "\:")


def format_input_id(input_id: str) -> str:
    """Format a user input ID.

    Args:
        input_id (str): The input ID

    Returns:
        str: The formatted input ID.
    """
    return str(input_id).replace('"', "").replace("'", "")


def write_title_info_toggle(
    title: str,
    info: str,
    element: st.delta_generator.DeltaGenerator,
):
    """Write a title (h1) followed by an "info" icon that toggles the
    visibility of a text when clicked. 

    Args:
        title (str): The title.
        info (str): The text to be displayed.
        element (st.delta_generator.DeltaGenerator): The streamlit element
            where the title and info will be written.
    """
    info = str(info).replace("\n", "")
    element.markdown(
        """
        <style>
            .toggle-el {
                padding: 2rem;
                transition: all 0.2s ease;
                opacity: 1;
                margin-top: 1rem;
                overflow: hidden;
            }
            input[type=checkbox].hide-input:not(:checked) ~ .toggle-el {
                height: 0;
                opacity: 0;
                padding-top: 0;
                padding-bottom: 0;
            }
            input.hide-input {
                position: absolute;
                left: -999em;
            }
            .title_info *{
                display: inline;
            }
            .circle {
                display: inline-flex;
                /* align-items: center; */
                justify-content: center;
                width: 18px;
                height: 18px;
                border-radius: 50%;
                border: 1px solid #0e1b17db;
                box-sizing: border-box;
                box-shadow: 0 0 0 1px #ebebebe3;
                background-color: transparent;
                transform: translate(-35px, -23px);
            }
            .circle label {
                font-size: 11px;
                cursor: pointer;
            }
        </style>
        """ +
        f"""
        <div class="title_info">
            <h1>{title}</h1>
            <div class="circle">
                <label for="item-3">❔<label/>
            </div>
        </div>
        <input type="checkbox" name="one" id="item-3" class="hide-input">
        <div class="toggle-el">
            <p>{info}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
