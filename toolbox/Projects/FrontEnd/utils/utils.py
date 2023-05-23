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

def format_id(ngsi_id: str) -> str:
    """Format an NGSI-LD entity ID for streamlit.

    Args:
        ngsi_id (str): An NGSI-LD entity ID.

    Returns:
        str: The formatted entity ID.
    """
    return ngsi_id.replace(":", "\:")
