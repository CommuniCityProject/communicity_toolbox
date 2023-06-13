from pathlib import Path
from typing import Literal, Optional

import cv2
import numpy as np
import torch
import torch.nn as nn

from toolbox.Structures import BoundingBox, Instance

from .box_utils import decode, decode_landm
from .config import cfg_mnet, cfg_re50
from .prior_box import PriorBox
from .py_cpu_nms import py_cpu_nms
from .retinaface import RetinaFace


class FaceDetector:
    """RetinaFace face detector.
    """

    def __init__(
        self,
        weights_path: Path,
        model_name: Literal["mobile0.25", "resnet50"],
        confidence_threshold: float = 0.7,
        landmarks: bool = False,
        nms_threshold: Optional[float] = 0.4,
        max_input_size: Optional[int] = None,
        use_cuda: bool = False
    ):
        """Create the face detector.

        Args:
            weights_path (Path): Path to the model weights file.
            model_name (Literal["mobile0.25", "resnet50"]): The model backbone
                name. One of "mobile0.25" or "resnet50".
            confidence_threshold (float, optional): The minimum detection
                confidence. Defaults to 0.7.
            landmarks (bool, optional): Process the face landmarks.
                Defaults to False.
            nms_threshold (Optional[float], optional):
                Non-maximum-suppression threshold. None to disable. Defaults
                to 0.4.
            max_input_size (Optional[int], optional): Maximum size of the
                image larger side. If None it is ignored. Defaults to None. 
            use_cuda (bool, optional): Run the model on a CUDA device.
                Defaults to False.

        Raises:
            ValueError: If ``model_name`` is not one of "mobile0.25" or
                "resnet50".
        """
        torch.set_grad_enabled(False)

        self._confidence_threshold = confidence_threshold
        self._parse_landmarks = landmarks
        self._nms_threshold = nms_threshold
        self._max_input_size = max_input_size

        if model_name == "mobile0.25":
            self._cfg = cfg_mnet
        elif model_name == "resnet50":
            self._cfg = cfg_re50
        else:
            raise ValueError("``model_name`` should be one of 'mobile0.25' "
                             "or 'resnet50'")

        self._net = RetinaFace(cfg=self._cfg, phase="test")
        self._net = self._load_model(self._net, weights_path, use_cuda)
        self._net.eval()
        self._device = torch.device("cuda" if use_cuda else "cpu")
        self._net = self._net.to(self._device)

    def _preprocess_image(self, image: np.ndarray) -> torch.tensor:
        """Preprocess an image for the model.

        Args:
            image (np.ndarray): A BGR uint8 image of shape (H, W, 3).

        Returns:
            torch.tensor: The image normalized with shape (1, 3, H, W).
        """
        image = image.astype(np.float32)
        image -= (104, 117, 123)
        image = image.transpose(2, 0, 1)
        image = torch.from_numpy(image).unsqueeze(0)
        image = image.to(self._device)
        return image

    def _scale_input_image(self, image: np.ndarray) -> np.ndarray:
        """Scale down an image if its larger side is greater than
        ``self._max_input_size``.

        Args:
            image (np.ndarray): The image to scale.

        Returns:
            np.ndarray: The scaled image.
        """
        if self._max_input_size is None:
            return image
        h, w, _ = image.shape
        f = 1
        if h >= w and h > self._max_input_size:
            f = self._max_input_size / h
        elif w > h and w > self._max_input_size:
            f = self._max_input_size / w
        if f != 1:
            image = cv2.resize(image, None, fx=f, fy=f)
        return image

    def predict(self, image: np.ndarray):
        """Detect faces on an image and return its bounding boxes and landmarks.

        Args:
            image (np.ndarray): A BGR uint8 image of shape (H, W, 3).

        Returns:
            List[Instance]: List of Instances with the following fields:
                - bounding_box (BoundingBox): A BoundingBox object with the
                    position of the detected face.
                - confidence (float): The detection confidence.
                - landmarks (np.ndarray): Predicted face landmarks if
                    ``self.landmarks`` is set to True.
        """
        image = self._scale_input_image(image)
        h, w, _ = image.shape
        scale = torch.Tensor([w, h, w, h])
        scale = scale.to(self._device)
        input_img = self._preprocess_image(image)

        loc, conf, landmarks = self._net(input_img)

        # Parse boxes
        prior_box = PriorBox(self._cfg, image_size=(h, w))
        priors = prior_box.forward()
        priors = priors.to(self._device)
        prior_data = priors.data
        boxes = decode(loc.data.squeeze(0), prior_data, self._cfg['variance'])
        boxes = boxes * scale
        boxes = boxes.cpu().numpy()

        # Parse score
        scores = conf.squeeze(0).data.cpu().numpy()[:, 1]

        # Filter scores
        score_keep = np.where(scores > self._confidence_threshold)[0]
        boxes = boxes[score_keep]
        scores = scores[score_keep]

        # Parse landmarks
        if self._parse_landmarks:
            landmarks = decode_landm(
                landmarks.data.squeeze(0),
                prior_data,
                self._cfg['variance']
            )

            scale_lm = torch.Tensor([
                input_img.shape[3], input_img.shape[2], input_img.shape[3],
                input_img.shape[2], input_img.shape[3], input_img.shape[2],
                input_img.shape[3], input_img.shape[2], input_img.shape[3],
                input_img.shape[2]
            ])

            scale_lm = scale_lm.to(self._device)
            landmarks = landmarks * scale_lm
            landmarks = landmarks.cpu().numpy()
            landmarks = landmarks[score_keep]

        # NMS
        if self._nms_threshold is not None:
            order = scores.argsort()[::-1]
            boxes = boxes[order]
            scores = scores[order]
            bs = np.hstack(
                (boxes, scores[:, np.newaxis])).astype(np.float32, copy=False)
            nms_keep = py_cpu_nms(bs, self._nms_threshold)
            boxes = boxes[nms_keep]
            scores = scores[nms_keep]
            if self._parse_landmarks:
                landmarks = landmarks[order][nms_keep]

        instances = []
        for i, score in enumerate(scores):
            box = BoundingBox.from_absolute(
                round(boxes[i, 0]),
                round(boxes[i, 1]),
                round(boxes[i, 2]),
                round(boxes[i, 3]),
                image_width=w,
                image_height=h
            )
            inst = Instance().set("bounding_box", box).set("confidence", score)
            if self._parse_landmarks:
                inst.set("landmarks", landmarks[i])

            instances.append(inst)

        return instances

    def _remove_model_prefix(self, state_dict: dict, prefix: str) -> dict:
        """Remove prefix from the state dict parameter names.

        Args:
            state_dict (dict): The state dict.
            prefix (_type_): The prefix to remove.

        Returns:
            dict: A state dict with the prefix removed from the parameter names.
        """
        def f(x): return x.split(prefix, 1)[-1] if x.startswith(prefix) else x
        return {f(key): value for key, value in state_dict.items()}

    def _load_model(self, model: nn.Module, pretrained_path: Path,
                    use_cuda: bool = False) -> nn.Module:
        """Load the model weights.

        Args:
            model (nn.Module): The model.
            pretrained_path (Path): Path to the weights file.
            use_cuda (bool, optional): Load the model on a CUDA device.
                Defaults to False.

        Returns:
            nn.Module: The loaded model.
        """
        if use_cuda:
            device_id = torch.cuda.current_device()
            pretrained_dict = torch.load(
                pretrained_path,
                map_location=lambda storage, loc: storage.cuda(device_id)
            )
        else:
            pretrained_dict = torch.load(
                pretrained_path,
                map_location=lambda storage, loc: storage
            )
        if "state_dict" in pretrained_dict.keys():
            pretrained_dict = self._remove_model_prefix(
                pretrained_dict['state_dict'],
                'module.'
            )
        else:
            pretrained_dict = self._remove_model_prefix(
                pretrained_dict,
                'module.'
            )
        model.load_state_dict(pretrained_dict, strict=False)
        return model
