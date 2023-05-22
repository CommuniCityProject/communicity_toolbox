from typing import List, Union

import numpy as np

from toolbox import DataModels
from toolbox.utils.config_utils import update_dict
from toolbox.Visualization import utils
from toolbox.Visualization.Defaults import Defaults


def draw(
    image: np.ndarray,
    data_models: Union[
        List[DataModels.InstanceSegmentation],
        DataModels.InstanceSegmentation
    ],
    config: dict
) -> np.ndarray:
    """Draw data from one or more InstanceSegmentation data models on an
    image.

    Args:
        image (np.ndarray): The image where draw the data.
        dms (Union[List[DataModels.InstanceSegmentation],
            DataModels.InstanceSegmentation]): A list or a single
            InstanceSegmentation data model.
        config (dict): A configuration dict.

    Returns:
        np.ndarray: The input image with the data models drawn.
    """
    config = update_dict(Defaults.dict(), config)

    if not isinstance(data_models, (list, tuple)):
        data_models = [data_models]

    # 1. Masks
    for dm in data_models:
        seg = dm.mask.resize(image.shape[1], image.shape[0])
        image = utils.draw_mask(
            image,
            seg,
            label_id=dm.label_id,
            color=config["mask_color"],
            alpha=config["mask_alpha"],
            colors_list=config["mask_colors_list"],
            color_by_label=config["mask_color_by_label"]
        )
    # 2. Bounding boxes
    if config["mask_show_box"]:
        for dm in data_models:

            text = ""
            if config["mask_show_label"]:
                text += f"{dm.label}"
            if config["mask_show_conf"]:
                if text:
                    text += f" ({dm.confidence:.2f})"
                else:
                    text += f"{dm.confidence:.2f}"
            text = text + "\n" if text else ""

            image = utils.draw_bounding_box(
                image=image,
                box=dm.bounding_box,
                thickness=config["box_thickness"],
                color=config["box_color"],
                text=text,
                text_scale=config["text_scale"],
                text_thickness=config["text_thickness"],
                text_color=config["text_color"],
                text_background=config["text_background"],
                text_bg_alpha=config["text_bg_alpha"],
                text_bg_color=config["text_bg_color"],
                text_line_space=config["text_line_space"],
                text_direction=utils.TextPosition[
                    str(config["text_direction"])],
                text_box_position=utils.TextPosition[
                    str(config["box_text_position"])],
            )
    return image
