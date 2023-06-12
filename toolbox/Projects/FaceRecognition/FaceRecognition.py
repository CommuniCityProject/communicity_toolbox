from pathlib import Path
from typing import List

import numpy as np
from toolbox import DataModels
from toolbox.Models import model_catalog
from toolbox.Structures import Image
from toolbox.utils.utils import get_logger

logger = get_logger("toolbox.FaceRecognition")


class FaceRecognition:
    """Perform face recognition on images.

    Attributes:
        domain (str): Name of the group of people to recognize.
        unknown_label (str): Name to set when a face is not recognized.
    """

    def __init__(self, config: dict, do_extraction: bool = False,
                 do_recognition: bool = False):
        """Initialize the models.

        Args:
            config (dict): Configuration dict.
            do_extraction (bool): Enable the prediction of features.
                Defaults to False.
            do_recognition (bool): Enable the recognition of features.
                Defaults to False.
        """
        rec_model = config["face_recognition"]["model_name"]
        rec_params = config["face_recognition"]["params"]
        logger.debug(f"Face recognition params {config['face_recognition']}")
        self._face_recognition = model_catalog[rec_model](**rec_params)

        self._do_extraction = do_extraction
        self._do_recognition = do_recognition

        if do_extraction:
            logger.info("Loading face recognition model")
            self._face_recognition.load_model()

            face_model = config["face_detector"]["model_name"]
            face_params = config["face_detector"]["params"]
            logger.info(f"Loading face detector model: {face_model}")
            logger.debug(f"Face detector params {face_params}")
            self._face_detector = model_catalog[face_model](**face_params)

        if do_recognition:
            self.load_dataset(Path(config["face_recognition"]["dataset_path"]))

        self.domain = config["face_recognition"].get("domain", "")
        self.unknown_label = config["face_recognition"].get(
            "unknown_label", "")

    def update_face(self, image: Image, face: DataModels.Face
                    ) -> DataModels.Face:
        """Extract and update the features attributes of a face data model.

        Args:
            image (toolbox.Structures.Image): An Image object.
            face (DataModels.Face): A DataModels.Face object.

        Returns:
            DataModels.Face: The same Face data model with the features
                attributes updated.
        """
        image = image.image
        bb = face.bounding_box
        if bb is not None:
            image = bb.crop_image(image)
        features = self._face_recognition.predict_features(image)
        face.features = features.tolist()
        face.features_algorithm = self._face_recognition.algorithm_name
        return face

    def predict(self, image: Image
                ) -> List[DataModels.Face]:
        """Extract features from an image, but do not recognize it.

        Args:
            image (toolbox.Structures.Image): An Image object.

        Returns:
            List[DataModels.Face]: A list of Face objects.
        """
        data_models = []

        face_instances = self._face_detector.predict(image.image)
        for face_ins in face_instances:
            crop = face_ins.bounding_box.crop_image(image.image)
            features = self._face_recognition.predict_features(crop)
            data_models.append(
                DataModels.Face(
                    bounding_box=face_ins.bounding_box,
                    detection_confidence=float(face_ins.confidence),
                    features=features.tolist(),
                    features_algorithm=self._face_recognition.algorithm_name,
                    image=image.id
                )
            )

        return data_models

    def recognize(self, face: DataModels.Face) -> DataModels.Face:
        """Recognize the features of a Face data model.

        Args:
            data_model (DataModels.Face): A Face object.

        Returns:
            DataModels.Face: A copy of the Face data model with the
                recognition data updated.
        """
        instances = self._face_recognition.recognize_features(
            np.array(face.features)
        )
        face.recognized_person = instances[0].name \
            if instances else self.unknown_label
        face.recognized_distance = instances[0].distance if instances else -1
        face.recognized = True
        face.recognition_domain = self.domain
        return face

    def register_features(self, face: DataModels.Face,
                          name: str):
        """Register the features of a Face DataModels to the given
        name.

        Args:
            face (DataModels.Face): A Face object
                with the predicted features.
            name (str): The name to which assign the given features.
        """
        self._face_recognition.add_features(name, face.features)

    def save_dataset(self, path: Path):
        """Save the current face features dataset to a file.

        Args:
            path (Path): Output pickle file path, ending in ".pkl".
        """
        self._face_recognition.save_features(path)

    def load_dataset(self, path: Path):
        """Load the dataset features from a pkl file.

        Args:
            path (Path): Path to the dataset pkl file.
        """
        self._face_recognition.load_features(path)

    @property
    def do_extraction(self) -> bool:
        return self._do_extraction

    @property
    def do_recognition(self) -> bool:
        return self._do_recognition
