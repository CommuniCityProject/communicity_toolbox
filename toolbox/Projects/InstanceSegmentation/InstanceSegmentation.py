from typing import List

from toolbox.Models import model_catalog
from toolbox import DataModels
from toolbox.Structures import Image
from toolbox.utils.utils import get_logger

logger = get_logger("toolbox.InstanceSegmentation")



class InstanceSegmentation:
    """Perform instance segmentation on images.
    """

    def __init__(self, config: dict):
        """Initialize the model.

        Args:
            config (dict): Configuration dict.
        """
        model_name = config["instance_segmentation"]["model_name"]
        model_params = config["instance_segmentation"]["params"]
        logger.info(f"Loading Instance segmentation model: {model_name}")
        logger.debug(f"Instance segmentation params: {model_params}")
        self._predictor = model_catalog[model_name](**model_params)
    
    def predict(self, image: Image
        ) -> List[DataModels.InstanceSegmentation]:
        """Perform instance segmentation on an image.

        Args:
            image (toolbox.Structures.Image): An Image object.
        
        Returns:
            List[DataModels.InstanceSegmentation]: A list of
                InstanceSegmentation objects.
        """
        instances = self._predictor.predict(image.image)

        data_models = []
        for ins in instances:
            data_models.append(
                DataModels.InstanceSegmentation(
                    mask=ins.mask,
                    bounding_box=ins.bounding_box,
                    label=ins.label,
                    label_id=ins.label_id,
                    confidence=ins.confidence,
                    image=image.id
                )
            )

        return data_models
