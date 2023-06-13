import os
from pathlib import Path
from typing import List, Union

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.compat.v1.keras.backend import set_session
from tensorflow.keras.models import load_model

from toolbox.Structures import Emotion, Instance


class EmotionsClassifier:
    """Perform classification of emotions on face images.
    """

    def __init__(self, model_path: Path, use_cuda: bool = False):
        """Load the emotions classifier.

        Args:
            model_path (Path): Path to the .h5 model file.
            use_cuda (bool, optional): If True, execute the model on
                a CUDA device. Defaults to False.
        """
        if not use_cuda:
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

        # Prevent the allocation of all the available GPU memory
        gpu_options = tf.compat.v1.GPUOptions(allow_growth=True)
        self._session = tf.compat.v1.Session(
            config=tf.compat.v1.ConfigProto(gpu_options=gpu_options)
        )

        set_session(self._session)
        self._model = load_model(str(model_path))

        self.idx_to_class = {
            0: Emotion.ANGER,
            1: Emotion.DISGUST,
            2: Emotion.FEAR,
            3: Emotion.HAPPINESS,
            4: Emotion.NEUTRAL,
            5: Emotion.SADNESS,
            6: Emotion.SURPRISE
        }

    def _preprocess_image(self, images: Union[List[np.ndarray], np.ndarray]
                          ) -> np.ndarray:
        """Preprocess the images for the model.

        Args:
            images (Union[List[np.ndarray], np.ndarray]): A list of images or
                a single image, BGR uint8 of shape (H, W, 3).

        Returns:
            np.ndarray: A preprocessed image of shape (B, 224, 224, 3)
        """
        if isinstance(images, np.ndarray) and images.ndim == 3:
            images = [images]

        batch = np.empty((len(images), 224, 224, 3), np.float32)
        for i, img in enumerate(images):
            resize_img = cv2.resize(img, (224, 224))
            batch[i] = resize_img
        batch[..., 0] -= 103.939
        batch[..., 1] -= 116.779
        batch[..., 2] -= 123.68
        return batch

    def predict(self, images: Union[List[np.ndarray], np.ndarray]
                ) -> List[Instance]:
        """Predict the emotion of a face image.

        Args:
            images (Union[List[np.ndarray], np.ndarray]): A single image or a
                list of images of faces, BGR uint8 of shape (H, W, 3).

        Returns:
            List[Instance]: List of Instances with an "emotion" field storing
                a ``Emotion`` enum and a "confidence" field storing the
                classification confidence. 
        """
        batch = self._preprocess_image(images)
        output = self._model.predict(batch)
        instances = []
        for out in output:
            emotion_id = np.argmax(out)
            emotion = self.idx_to_class[emotion_id]
            conf = out[emotion_id]
            instances.append(
                Instance().set("emotion", emotion).set("confidence", conf)
            )
        return instances
