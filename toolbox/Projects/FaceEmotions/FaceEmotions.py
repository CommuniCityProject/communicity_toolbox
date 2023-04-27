from typing import List

from toolbox.Models import model_catalog
from toolbox import DataModels
from toolbox.Structures import Image, BoundingBox
from toolbox.utils.utils import get_logger

logger = get_logger("toolbox.FaceEmotions")



class FaceEmotions:
    """Detect faces on images and predict its emotion.
    
    Methods:
        update_face(image, face) -> DataModels.Face
        predict(image) -> List[DataModels.Face]
    """

    def __init__(self, config: dict):
        """Initialize the models.

        Args:
            config (dict): Configuration dict.
        """
        emo_model = config["face_emotions"]["model_name"]
        emo_params = config["face_emotions"]["params"]
        logger.info(f"Loading age-gender model: {emo_model}")
        logger.debug(f"Age-gender params: {emo_params}")
        self._emotions_classifier = model_catalog[emo_model](**emo_params)

        face_model = config["face_detector"]["model_name"]
        face_params = config["face_detector"]["params"]
        logger.info(f"Loading face detector model: {face_model}")
        logger.debug(f"Face detector params {face_params}")
        self._face_detector = model_catalog[face_model](**face_params)
        self._scale_bb = config["face_detector"]["face_box_scale"]
    
    def update_face(self, image: Image, face: DataModels.Face
        ) -> DataModels.Face:
        """Predict the emotion of a face data model.

        Args:
            face (DataModels.Face): A DataModels.Face object.

        Returns:
            DataModels.Face: The same Face data model with the emotions
                attributes updated.
        """
        image = image.image
        bb = face.bounding_box
        if bb is not None:
            scaled_bb = bb.scale(self._scale_bb)
            if scaled_bb.is_empty():
                return face
            image = scaled_bb.crop_image(image)
        emo_instance = self._emotions_classifier.predict(image)[0]
        face.emotion = emo_instance.emotion
        face.emotion_confidence = float(emo_instance.confidence)
        return face

    def predict(self, image: Image) -> List[DataModels.Face]:
        """Predicts the position and the emotion of faces on an image.

        Args:
            image (Image): An Image object.

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
            emo_instance = self._emotions_classifier.predict(face_crop)[0]
            dm = DataModels.Face(
                bounding_box=bb,
                detection_confidence=float(face_instance.confidence),
                emotion=emo_instance.emotion,
                emotion_confidence=float(emo_instance.confidence),
                image=image.id
            )
            data_models.append(dm)

        return data_models
