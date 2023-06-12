from typing import List

from toolbox.Models import model_catalog
from toolbox import DataModels
from toolbox.Structures import Image, BoundingBox
from toolbox.utils.utils import get_logger

logger = get_logger("toolbox.FaceDetection")



class FaceDetection:
    """Detect faces on images.
    """

    def __init__(self, config: dict):
        """Initialize the models.

        Args:
            config (dict): Configuration dict.
        """
        model_name = config["face_detector"]["model_name"]
        model_params = config["face_detector"]["params"]
        logger.info(f"Loading face detector model: {model_name}")
        logger.debug(f"Face detector params {model_params}")
        self._face_detector = model_catalog[model_name](**model_params)

    def predict(self, image: Image) -> List[DataModels.Face]:
        """Predicts the position of faces on an image.

        Args:
            image (toolbox.Structures.Image): An Image object.

        Returns:
            List[DataModels.Face]: A list of Face data models.
        """
        face_instances = self._face_detector.predict(image.image)
        
        data_models = []
        for face_instance in face_instances:
            bb: BoundingBox = face_instance.bounding_box
            if bb.is_empty():
                continue
            dm = DataModels.Face(
                bounding_box=bb,
                detection_confidence=float(face_instance.confidence),
                image=image.id
            )
            data_models.append(dm)

        return data_models
