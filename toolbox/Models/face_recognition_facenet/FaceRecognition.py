import os
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import cv2
import numpy as np
import tensorflow as tf

from toolbox.Structures import Instance

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class FaceRecognition:
    """Perform face recognition. Extract features from face images and compare
    them with a local dataset.

        Attributes:
        distance_threshold (float): Maximum distance between two
            features vector to consider them from the same person.
    """

    __algorithm_name__ = "FaceNet"

    def __init__(self, distance_threshold: float = 0.75,
                 model_path: Optional[Path] = None, use_cuda: bool = False):
        """Create the FaceRecognition model.

        Args:
            distance_threshold (float, optional): Maximum distance between two
                features vector to consider them from the same person.
                Defaults to 0.75.
            model_path (Optional[Path], optional): Path to the model checkpoint.
                (.ckpt-..., without the ".data-..."). Defaults to None.
            use_cuda (bool, optional): Execute the model on a cuda device.
                Defaults to False.
        """
        self.distance_threshold = distance_threshold
        self._model_path = model_path
        self._use_cuda = use_cuda
        self._session = None
        self._face_features: Dict[str, np.ndarray] = {}

    def load_model(self):
        """Load the model from a checkpoint file.
        """
        if self._model_path is None:
            raise ValueError("Model path is not defined")
        
        model_path = Path(self._model_path)
        
        if not self._use_cuda:
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

        tf.compat.v1.disable_eager_execution()

        # Prevent the allocation of all the available GPU memory
        gpu_options = tf.compat.v1.GPUOptions(allow_growth=True)
        self._session = tf.compat.v1.Session(
            config=tf.compat.v1.ConfigProto(gpu_options=gpu_options)
        )

        # Load the model
        saver = tf.compat.v1.train.import_meta_graph(
            str(model_path.with_suffix(".meta"))
        )
        saver.restore(self._session, str(model_path))

        self._net_embeddings = tf.compat.v1.get_default_graph(). \
            get_tensor_by_name("embeddings:0")
        self._image_placeholder = tf.compat.v1.get_default_graph(). \
            get_tensor_by_name("input:0")
        self._phase_train_placeholder = tf.compat.v1.get_default_graph(). \
            get_tensor_by_name("phase_train:0")

    def predict_features(self, image: np.ndarray) -> np.ndarray:
        """Predict a face image and extract a features vector.

        Args:
            image (np.ndarray): A BGR uint8 image of shape (H, W, 3) of a face.

        Raises:
            ValueError: If the model is not loaded (call 'load_model()').

        Returns:
            np.ndarray: The predicted features vector.
        """
        if self._session is None:
            raise ValueError("Model is not loaded")

        # Normalize the image
        image = cv2.resize(image, (160, 160))
        std_adj = np.maximum(np.std(image), 1.0 / np.sqrt(image.size))
        image = (image - np.mean(image)) / std_adj
        image = np.expand_dims(image, axis=0)

        # Predict
        feed_dict = {
            self._image_placeholder: image,
            self._phase_train_placeholder: False
        }
        out = self._session.run(self._net_embeddings, feed_dict=feed_dict)[0]
        return out

    def load_features(self, features_path: Path):
        """Load face features from a pickle file.

        Args:
            features_path (Path): Path to a pickle file (.pkl).
        """
        with open(features_path, "rb") as f:
            self._face_features = pickle.load(f)

    def add_features(self, name: str, features: np.ndarray):
        """Store a new features vector.

        Args:
            name (str): Name associated with the features.
            features (np.ndarray): A features vector.
        """
        self._face_features[name] = features

    def save_features(self, path: Path):
        """Save the current face features to a file.

        Args:
            path (Path): Output pickle file path, ending in ".pkl".
        """
        with open(path, "wb") as f:
            pickle.dump(self._face_features, f)

    def _compare(self, f1: np.ndarray, f2: np.ndarray) -> Tuple[bool, float]:
        """Compare two features vectors.

        Args:
            f1 (np.ndarray): Feature vector.
            f2 (np.ndarray): Feature vector.

        Returns:
            Tuple[bool, float]: A bool indicating if both features are similar
                and its euclidean distance.
        """
        dist = np.sum(np.square(f1 - f2))
        return dist < self.distance_threshold, dist

    def recognize_features(self, features: np.ndarray) -> List[Instance]:
        """Search a features vector in the stored face features.

        Args:
            features (np.ndarray): The features of a face.

        Returns:
            List[Instance]: A list of Instance sorted from most to least
                similar, with the following fields:
                - name (str): The name of the recognized face.
                - distance (float): The euclidean distance from the supplied
                features to the recognized features.
        """
        recognized = {}
        for name, c_features in self._face_features.items():
            eq, dist = self._compare(features, c_features)
            if eq:
                recognized[name] = dist

        # Create instances with the recognized faces, sorted from most to
        # least similar.
        instances = []
        for name, dist in sorted(list(recognized.items()), key=lambda x: x[1]):
            instances.append(Instance().set(
                "name", name).set("distance", dist))
        return instances

    def recognize_image(self, image: np.ndarray) -> List[Instance]:
        """Recognize a face.

        Args:
            image (np.ndarray): A BGR uint8 image of shape (H, W, 3) of a face.

        Returns:
            List[Instance]: A list of Instance sorted from most to least
                similar, with the following fields:
                - name (str): The name of the recognized face.
                - distance (float): The euclidean distance from the supplied
                features to the recognized features.
        """
        features = self.predict_features(image)
        instances = self.recognize_features(features)
        return instances

    @property
    def algorithm_name(self) -> str:
        """Get the name of the face recognition algorithm.
        """
        return self.__algorithm_name__