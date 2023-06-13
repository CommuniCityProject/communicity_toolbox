from typing import List

from toolbox import DataModels
from toolbox.Models import model_catalog
from toolbox.Structures import BoundingBox, Image
from toolbox.utils.utils import float_or_none, get_logger

logger = get_logger("toolbox.AgeGender")


class AgeGender:
    """Detect faces on images and predict its age and gender.
    """

    def __init__(self, config: dict):
        """Initialize the models.

        Args:
            config (dict): Configuration dict.
        """
        ag_model = config["age_gender"]["model_name"]
        ag_params = config["age_gender"]["params"]
        logger.info(f"Loading age-gender model: {ag_model}")
        logger.debug(f"Age-gender params: {ag_params}")
        self._ag_predictor = model_catalog[ag_model](**ag_params)

        face_model = config["face_detector"]["model_name"]
        face_params = config["face_detector"]["params"]
        logger.info(f"Loading face detector model: {face_model}")
        logger.debug(f"Face detector params {face_params}")
        self._face_detector = model_catalog[face_model](**face_params)
        self._scale_bb = config["face_detector"]["face_box_scale"]

    def update_face(self, image: Image, face: DataModels.Face
                    ) -> DataModels.Face:
        """Predict the age and gender of a face data model.

        Args:
            image (toolbox.Structures.Image): An Image object.
            face (DataModels.Face): A Face data model object.

        Returns:
            DataModels.Face: The same Face data model with the age and gender
                attributes updated.
        """
        image = image.image
        bb = face.bounding_box
        if bb is not None:
            scaled_bb = bb.scale(self._scale_bb)
            if scaled_bb.is_empty():
                return face
            image = scaled_bb.crop_image(image)
        ag_instance = self._ag_predictor.predict(image)[0]
        face.age = float_or_none(ag_instance.get("age"))
        face.gender = ag_instance.get("gender")
        face.gender_confidence = float_or_none(
            ag_instance.get("gender_confidence"))
        assert face.gender is not None or face.age is not None, (
            face.gender, face.age)
        return face

    def predict(self, image: Image) -> List[DataModels.Face]:
        """Predict the position, age and gender of faces in an image.

        Args:
            image (toolbox.Structures.Image): An Image object.

        Returns:
            List[DataModels.Face]: A list of Face data models.
        """
        face_instances = self._face_detector.predict(image.image)

        data_models = []
        for face_instance in face_instances:
            bb: BoundingBox = face_instance.bounding_box
            scaled_bb = bb.scale(self._scale_bb)
            if scaled_bb.is_empty():
                continue
            face_crop = scaled_bb.crop_image(image.image)
            ag_instance = self._ag_predictor.predict(face_crop)[0]
            dm = DataModels.Face(
                bounding_box=bb,
                detection_confidence=float(face_instance.confidence),
                age=float(ag_instance.get("age")),
                gender=ag_instance.get("gender"),
                gender_confidence=float(ag_instance.get("gender_confidence")),
                image=image.id
            )
            data_models.append(dm)

        return data_models
