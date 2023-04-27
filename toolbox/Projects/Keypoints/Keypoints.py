from typing import List

from toolbox.Models import model_catalog
from toolbox.DataModels import PersonKeyPoints
from toolbox.Structures import Image
from toolbox.utils.utils import get_logger

logger = get_logger("toolbox.Keypoints")



class Keypoints:
    """Predict person keypoints from images.
    
    Methods:
        predict(image) -> List[PersonKeyPoints]
    """

    def __init__(self, config: dict):
        """Initialize the model.

        Args:
            config (dict): A configuration dict.
        """
        model_name = config["keypoints"]["model_name"]
        model_params = config["keypoints"]["params"]
        logger.info(f"Loading Keypoints model: {model_name}")
        logger.debug(f"Keypoints params: {model_params}")
        self._predictor = model_catalog[model_name](**model_params)

    def predict(self, image: Image
        ) -> List[PersonKeyPoints]:
        """Predict person keypoints from an image.

        Args:
            image (Image): An Image object.
        
        Returns:
            List[PersonKeyPoints]: A list of PersonKeyPoints objects.
        """
        instances = self._predictor.predict(image.image)
        
        data_models = []
        for ins in instances:
            data_models.append(
                PersonKeyPoints(
                    bounding_box=ins.bounding_box,
                    confidence=ins.confidence,
                    keypoints=ins.keypoints,
                    image=image.id,
                )
            )

        return data_models
