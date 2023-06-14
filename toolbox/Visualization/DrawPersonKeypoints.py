from typing import List, Union

import numpy as np

from toolbox import DataModels
from toolbox.utils.config_utils import update_dict
from toolbox.Visualization import utils
from toolbox.Visualization.Defaults import (COCO_KEYPOINTS_COLORS,
                                            COCO_KEYPOINTS_CONNECTION_RULES,
                                            Defaults)


def draw(
    image: np.ndarray,
    data_models: Union[
        List[DataModels.PersonKeyPoints],
        DataModels.PersonKeyPoints
    ],
    config: dict
) -> np.ndarray:
    """Draw PersonKeyPoints data models data on an image.

    Args:
        image (np.ndarray): The image where draw the data.
        data_models (Union[List[DataModels.PersonKeyPoints], DataModels.PersonKeyPoints]):
            A list or a single PersonKeyPoints data model.
        config (dict): A configuration dict.

    Returns:
        np.ndarray: The input image with the data models drawn.
    """
    config = update_dict(Defaults.dict(), config)

    if not isinstance(data_models, (list, tuple)):
        data_models = [data_models]

    # 1. Keypoints
    for dm in data_models:
        image = utils.draw_coco_keypoints(
            image=image,
            keypoints=dm.keypoints,
            color=config["kp_color"],
            color_by_label=config["kp_color_by_label"],
            color_mapping=config["COCO_KEYPOINTS_COLORS"],
            keypoint_radius=config["kp_radius"],
            connection_rules=config["COCO_KEYPOINTS_CONNECTION_RULES"],
            line_thickness=config["kp_line_thickness"],
            show_names=config["kp_show_name"],
            show_conf=config["kp_show_conf"],
            show_keypoints=config["kp_show_kp"],
            show_connections=config["kp_show_connections"],
            text_scale=config["text_scale"],
            text_thickness=config["text_thickness"],
            text_color=config["text_color"],
            text_bg_color=config["text_bg_color"],
            text_bg_alpha=config["text_bg_alpha"],
        )
    # 2. Bounding boxes
    if config["kp_show_box"]:
        for dm in data_models:
            text = f"{dm.confidence:.2f}" \
                if config["kp_show_detection_conf"] else ""
            image = utils.draw_bounding_box(
                image=image,
                box=dm.bounding_box,
                text=text,
                thickness=config["box_thickness"],
                color=config["box_color"],
                text_scale=config["text_scale"],
                text_thickness=config["text_thickness"],
                text_color=config["text_color"],
                text_background=config["text_background"],
                text_bg_color=config["text_bg_color"],
                text_bg_alpha=config["text_bg_alpha"],
                text_line_space=config["text_line_space"],
                text_box_position=utils.TextPosition[str(
                    config["box_text_position"])],
                text_direction=utils.TextPosition[str(
                    config["text_direction"])]
            )
    return image
