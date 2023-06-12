from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
import onnxruntime as ort

from toolbox.Structures import BoundingBox, Instance

ort.set_default_logger_severity(3)


class FaceDetector:
    """UltraFace face detector.
    """

    def __init__(self, model_path: Path, input_size: Tuple[int, int],
                 confidence_threshold: float = 0.7, use_cuda: bool = False):
        """Create the face predictor and load the model.

        Args:
            model_path (Path): Path to the onnx model file.
            input_size (Tuple[int, int]): Model input size. (640, 480) or
                (320, 240).
            confidence_threshold (float, optional): Confidence threshold.
                Defaults to 0.7.
            use_cuda (bool, optional): If True, tries to execute the model on
                the GPU. Defaults to False.
        """
        self._input_size = tuple(input_size)
        self._confidence_thr = confidence_threshold

        provider = "CUDAExecutionProvider" if use_cuda \
            else "CPUExecutionProvider"
        self._detector = ort.InferenceSession(
            model_path,
            providers=[provider]
        )
        self._input_name = self._detector.get_inputs()[0].name

    def _area_of(self, left_top: np.ndarray, right_bottom: np.ndarray) -> float:
        """Compute the areas of rectangles given two corners.

        Args:
            left_top (np.ndarray): left top corner.
            right_bottom (np.ndarray): right bottom corner.

        Returns:
            int: the area.
        """
        hw = np.clip(right_bottom - left_top, 0.0, None)
        return hw[..., 0] * hw[..., 1]

    def _iou_of(self, boxes0: np.ndarray, boxes1: np.diagonal,
                eps: bool = 1e-5) -> np.ndarray:
        """Return intersection-over-union (Jaccard index) of boxes.

        Args:
            boxes0 (np.ndarray): ground truth boxes (N, 4).
            boxes1 (np.ndarray): predicted boxes (N or 1, 4).
            eps (float, optional): a small number to avoid 0 as denominator.
                Defaults to 1e-5.

        Returns:
            np.ndarray: IoU values (N).
        """
        overlap_left_top = np.maximum(boxes0[..., :2], boxes1[..., :2])
        overlap_right_bottom = np.minimum(boxes0[..., 2:], boxes1[..., 2:])

        overlap_area = self._area_of(overlap_left_top, overlap_right_bottom)
        area0 = self._area_of(boxes0[..., :2], boxes0[..., 2:])
        area1 = self._area_of(boxes1[..., :2], boxes1[..., 2:])
        return overlap_area / (area0 + area1 - overlap_area + eps)

    def _hard_nms(self, box_scores: np.ndarray, iou_threshold: float,
                  top_k: int = -1, candidate_size: int = 200) -> np.ndarray:
        """Perform hard non-maximum-suppression to filter out boxes with iou
        greater than threshold

        Args:
            box_scores (np.ndarray): boxes in corner-form and probabilities
                (N, 5).
            iou_threshold (float): intersection over union threshold.
            top_k (int, optional): keep top_k results. If k <= 0, keep all the
                results. Defaults to -1.
            candidate_size (int, optional): only consider the candidates with
                the highest scores. Defaults to 200.

        Returns:
            np.ndarray: a list of indexes of the kept boxes.
        """
        scores = box_scores[:, -1]
        boxes = box_scores[:, :-1]
        picked = []
        indexes = np.argsort(scores)
        indexes = indexes[-candidate_size:]
        while len(indexes) > 0:
            current = indexes[-1]
            picked.append(current)
            if 0 < top_k == len(picked) or len(indexes) == 1:
                break
            current_box = boxes[current, :]
            indexes = indexes[:-1]
            rest_boxes = boxes[indexes, :]
            iou = self._iou_of(
                rest_boxes,
                np.expand_dims(current_box, axis=0),
            )
            indexes = indexes[iou <= iou_threshold]

        return box_scores[picked, :]

    def _parse_boxes(self, width: int, height: int, confidences: np.ndarray,
                     boxes: np.ndarray, prob_threshold: float, iou_threshold: float = 0.5,
                     top_k: int = -1) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Select boxes that contain human faces.

        Args:
            width (int): Original image width.
            height (int): Original image height.
            confidences (np.ndarray): Confidence array (N, 2).
            boxes (np.ndarray): Boxes array in corner-form (N, 4).
            iou_threshold (float, optional): Intersection over union threshold.
                Defaults to 0.5.
            top_k (int): Keep top_k results. If k <= 0, keep all the results.
                Defaults to -1.

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]:
                boxes (k, 4): boxes to keep.
                labels (k): array of labels for each box.
                probs (k): an array of probabilities for each box.
        """
        assert boxes.shape[0] == 1
        assert confidences.shape[0] == 1
        boxes = boxes[0]
        confidences = confidences[0]

        picked_box_probs = []
        picked_labels = []
        for class_index in range(1, confidences.shape[1]):
            probs = confidences[:, class_index]
            mask = probs > prob_threshold
            probs = probs[mask]

            if probs.shape[0] == 0:
                continue

            subset_boxes = boxes[mask, :]
            box_probs = np.concatenate(
                [subset_boxes, probs.reshape(-1, 1)],
                axis=1
            )
            box_probs = self._hard_nms(
                box_probs,
                iou_threshold=iou_threshold,
                top_k=top_k,
            )
            picked_box_probs.append(box_probs)
            picked_labels.extend([class_index] * box_probs.shape[0])
        if not picked_box_probs:
            return np.array([]), np.array([]), np.array([])
        picked_box_probs = np.concatenate(picked_box_probs)
        picked_box_probs[:, 0] *= width
        picked_box_probs[:, 1] *= height
        picked_box_probs[:, 2] *= width
        picked_box_probs[:, 3] *= height
        return (
            picked_box_probs[:, :4].astype(np.int32),
            np.array(picked_labels),
            picked_box_probs[:, 4]
        )

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess an image for the model.

        Args:
            image (np.ndarray): A BGR uint8 image of shape (H, W, 3).

        Returns:
            np.ndarray: A normalized array of shape (1, 3, H, W).
        """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, self._input_size)
        image_mean = np.array([127, 127, 127])
        image = (image - image_mean) / 128
        image = np.transpose(image, [2, 0, 1])
        image = np.expand_dims(image, axis=0)
        image = image.astype(np.float32)
        return image

    def predict(self, image: np.ndarray) -> List[Instance]:
        """Detect faces on an image and return its bounding boxes.

        Args:
            image (np.ndarray): A BGR uint8 image of shape (H, W, 3).

        Returns:
            List[Instance]: A list of Instance with the following fields:
                bounding_box (BoundingBox): A BoundingBox object with the
                    position of the detected face
                confidence (float): The detection confidence.
        """
        instances = []
        input_image = self._preprocess_image(image)
        confidences, boxes = self._detector.run(
            None,
            {self._input_name: input_image}
        )
        boxes, labels, probs = self._parse_boxes(
            image.shape[1],
            image.shape[0],
            confidences,
            boxes,
            self._confidence_thr
        )

        boxes = [
            BoundingBox.from_absolute(
                b[0], b[1], b[2], b[3],
                image_width=image.shape[1],
                image_height=image.shape[0]
            )
            for b in boxes
        ]

        instances = [
            Instance().set("bounding_box", box).set("confidence", conf)
            for box, conf in zip(boxes, probs)
        ]
        return instances
