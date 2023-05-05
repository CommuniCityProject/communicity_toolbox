import copy
from typing import List, Optional, Union

import cv2
import numpy as np

from toolbox import DataModels
from toolbox.utils.config_utils import update_dict
from toolbox.Visualization import (DrawFace, DrawInstanceSegmentation,
                                   DrawPersonKeypoints)

DATA_MODEL_DRAWERS = {
    DataModels.Face: DrawFace,
    DataModels.InstanceSegmentation: DrawInstanceSegmentation,
    DataModels.PersonKeyPoints: DrawPersonKeypoints,
}


class DataModelVisualizer:
    """Class to visualize the data models.

    """

    def __init__(self, config: dict = {}):
        """
        Args:
            config (dict): Configuration dict with the optional visualization
                parameters.
        """
        self.set_config(config)

    def set_config(self, config: dict):
        self.config = config.get("visualization", {})
        self.config = {} if self.config is None else self.config
        self.img_w = self.config.get("image_width", None)
        self.img_h = self.config.get("image_height", None)

    def visualize_data_models(
        self,
        image: np.ndarray,
        data_models: Union[List[DataModels.BaseModel], DataModels.BaseModel],
        config: Optional[dict] = None
    ) -> np.ndarray:
        """Visualize a single or a list of data models.

        Args:
            image (np.ndarray): Image where draw the data models.
            data_models (Union[List[DataModels.BaseModel],
                DataModels.BaseModel]): A single or a list of any data model.
            config (Optional[dict]): Optional configuration dict that will
                override the base config. Defaults to None.

        Returns:
            np.ndarray: A copy of the original image with the data drawn.
        """
        if config is not None:
            config = update_dict(copy.deepcopy(self.config), config)
        else:
            config = self.config

        if not isinstance(data_models, (list, tuple)):
            data_models = [data_models]

        image = image.copy()
        orig_h, orig_w = image.shape[:2]

        fx = None
        fy = None
        if (self.img_w is not None and self.img_w != orig_w) or \
                (self.img_h is not None and self.img_h != orig_h):

            fx = self.img_w / orig_w if self.img_w is not None else None
            fy = self.img_h / orig_h if self.img_h is not None else None
            fx = fx if fx is not None else fy
            fy = fy if fy is not None else fx

            image = cv2.resize(image, None, fx=fx, fy=fy)

        class_dms = {}
        for dm in data_models:
            class_dms.setdefault(type(dm), []).append(dm)

        for dm_type, dms in class_dms.items():
            image = DATA_MODEL_DRAWERS[dm_type].draw(
                image, dms, config)

        return image
