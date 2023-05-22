import ast

import streamlit as st

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
