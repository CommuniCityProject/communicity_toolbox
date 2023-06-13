from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np
from scipy.special import softmax

from toolbox.Structures import Gender, Instance


class AgeGenderPredictor:
    """Predict the age and gender of a face image.
    """

    def __init__(self, age_model_path: Optional[Path] = None,
                 gender_model_path: Optional[Path] = None, do_age: bool = True,
                 do_gender: bool = True, use_cuda: bool = False):
        """Create and load the age and gender models.

        Args:
            age_model_path (Optional[Path], optional): Path to the onnx age
                model. Defaults to None.
            gender_model_path (Optional[Path], optional): Path to the onnx
                gender model. Defaults to None.
            do_age (bool, optional): Enable the age prediction.
                Defaults to True.
            do_gender (bool, optional): Enable the age prediction.
                Defaults to True.
            use_cuda (bool, optional): If True, execute the model on a CUDA
                device. Defaults to False.
        """
        if not do_age and not do_gender:
            raise ValueError("``do_age`` or ``do_gender`` must be True")
        self._do_age = do_age
        self._do_gender = do_gender

        if do_age:
            self._age_model = cv2.dnn.readNetFromONNX(str(age_model_path))
            if use_cuda:
                self._enable_cuda_model(self._age_model)
        if do_gender:
            self._gender_model = cv2.dnn.readNetFromONNX(
                str(gender_model_path))
            if use_cuda:
                self._enable_cuda_model(self._gender_model)

    def _enable_cuda_model(self, model: cv2.dnn.Net):
        """Set the model preferable execution device to cuda.
        """
        model.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        model.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    def _preprocess_image(self, images: Union[List[np.ndarray], np.ndarray]
                          ) -> np.ndarray:
        """Preprocess the images for the model.

        Args:
            images (Union[List[np.ndarray], np.ndarray]): A list of images or
                a single image, BGR uint8 of shape (H, W, 3).

        Returns:
            np.ndarray: A preprocessed array of shape (B, 3, 224, 224)
        """
        if isinstance(images, np.ndarray) and images.ndim == 3:
            images = [images]

        input_blob = np.zeros((len(images), 3, 224, 224))
        for i, img in enumerate(images):
            img = cv2.resize(img, (224, 224))
            input_blob[i] = img.transpose(2, 0, 1)
        return input_blob

    def _predict_age(self, input_blob: np.ndarray) -> List[float]:
        """Predict the age.

        Args:
            input_blob (np.ndarray): Input blob of shape (B, 3, 224, 224)

        Returns:
            List[float]: List of ages.
        """
        self._age_model.setInput(input_blob)
        ages = self._age_model.forward()
        ages = softmax(ages, axis=1)
        ages = ages * np.arange(101, dtype=np.float32)
        ages = np.sum(ages, axis=1)
        return ages

    def _predict_gender(self, input_blob: np.ndarray
                        ) -> Tuple[List[Gender], np.ndarray]:
        """Predict the gender.

        Args:
            input_blob (np.ndarray): Input blob of shape (B, 3, 224, 224).

        Returns:
            Tuple[List[Gender], np.ndarray]: List of genders and list of
                confidences.
        """
        self._gender_model.setInput(input_blob)
        output = self._gender_model.forward()
        output = softmax(output, axis=1)
        genders = np.argmax(output, axis=1)
        confidences = output[:, genders].flatten()
        genders = [
            Gender.MALE if g else
            Gender.FEMALE
            for g in genders
        ]
        return genders, confidences

    def predict_age(self, images: Union[List[np.ndarray], np.ndarray]
                    ) -> List[Instance]:
        """Predict the age of a face image.

        Args:
            images (Union[List[np.ndarray], np.ndarray]): A single image or a
                list of images of face crops, BGR uint8 of shape (H, W, 3).

        Raises:
            ValueError: If ``do_age`` is set to False.

        Returns:
            List[Instance]: A list of Instances with a float-type "age" field.
        """
        if not self._do_age:
            raise ValueError(
                "Age model is not loaded because ``do_age`` was set to False"
            )
        input_blob = self._preprocess_image(images)
        ages = self._predict_age(input_blob)
        return [Instance().set("age", age) for age in ages]

    def predict_gender(self, images: Union[List[np.ndarray], np.ndarray]
                       ) -> List[Instance]:
        """Predict the gender of a face image

        Args:
            images (Union[List[np.ndarray], np.ndarray]): A single image or a
                list of images of face crops, BGR uint8 of shape (H, W, 3).

        Raises:
            ValueError: If ``do_gender`` is set to False.

        Returns:
            List[Instance]: A list of Instances with a "gender" field storing a
                Gender enum and a "confidence" field storing the gender
                classification confidence. 
        """
        if not self._do_gender:
            raise ValueError(
                "Gender model is not loaded because ``do_gender`` was set "
                "to False"
            )
        input_blob = self._preprocess_image(images)
        genders, confidences = self._predict_gender(input_blob)
        return [
            Instance().set("gender", gen).set("confidence", conf)
            for gen, conf in zip(genders, confidences)
        ]

    def predict(self, images: Union[List[np.ndarray], np.ndarray]
                ) -> List[Instance]:
        """Predict the age and gender of the faces on an image.

        Args:
            images (Union[List[np.ndarray], np.ndarray]): A single image or a
                list of face images, BGR uint8 of shape (H, W, 3).

        Returns:
            List[Instance]: An Instance for each image with the following fields:
                - age (float): The age of the face (if ``do_age`` is True).
                - gender (Gender): A Gender enum (if ``do_gender`` is True).
                - gender_confidence (float) The gender confidence
                    (if ``do_gender`` is True).
        """
        input_blob = self._preprocess_image(images)
        instances = [Instance() for _ in range(len(input_blob))]

        if self._do_age:
            ages = self._predict_age(input_blob)
            [ins.set("age", age) for ins, age in zip(instances, ages)]

        if self._do_gender:
            genders, confidences = self._predict_gender(input_blob)
            [ins.set("gender", gender).set("gender_confidence", conf)
             for ins, gender, conf in zip(instances, genders, confidences)]

        return instances
