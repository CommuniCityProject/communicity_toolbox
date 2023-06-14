from typing import List, Union

import numpy as np

from toolbox import DataModels
from toolbox.Structures import BoundingBox
from toolbox.utils.config_utils import update_dict
from toolbox.Visualization import utils
from toolbox.Visualization.Defaults import Defaults


def draw(
    image: np.ndarray,
    data_models: Union[List[DataModels.Face], DataModels.Face],
    config: dict
) -> np.ndarray:
    """Draw data form one or more Face data models on an image.

    Args:
        image (np.ndarray): The image where draw the data.
        data_models (Union[List[DataModels.Face], DataModels.Face]): A list or
            a single Face data model.
        config (dict): A configuration dict.

    Returns:
        np.ndarray: The input image with the data models drawn.
    """
    config = update_dict(Defaults.dict(), config)

    if not isinstance(data_models, (list, tuple)):
        data_models = [data_models]

    for dm in data_models:
        text = ""

        # Bounding box
        bb = BoundingBox(
            0, 0, 1, 1) if dm.bounding_box is None else dm.bounding_box

        # Face detection confidence
        if dm.detection_confidence is not None and config["face_show_conf"]:
            text += f"{dm.detection_confidence:.2f}\n"

        # Age
        if dm.age is not None and config["face_show_age"]:
            text += f"Age: {int(dm.age)}\n"

        # Gender
        if dm.gender is not None and config["face_show_gender"]:
            text += f"Gender: {dm.gender}"
            if config["face_show_gender_conf"]:
                text += f" ({dm.gender_confidence:.2f})\n"
            else:
                text += "\n"

        # Emotion
        if dm.emotion is not None and config["face_show_emotion"]:
            text += f"Emotion: {dm.emotion}"
            if config["face_show_emotion_conf"]:
                text += f" ({dm.emotion_confidence:.2f})\n"
            else:
                text += "\n"

        # Recognition
        if dm.recognized and config["face_show_recognized_person"]:
            text += f"{dm.recognized_person}"
            if config["face_show_recognized_dist"]:
                text += f" ({dm.recognized_distance:.2f})\n"
            else:
                text += "\n"

        image = utils.draw_bounding_box(
            image=image,
            box=bb,
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
            text_direction=utils.TextPosition[str(config["text_direction"])]
        )
    return image
