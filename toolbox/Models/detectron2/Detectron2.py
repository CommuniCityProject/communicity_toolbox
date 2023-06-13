from pathlib import Path
from typing import List, Optional

import numpy as np
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.engine.defaults import DefaultPredictor

from toolbox.Structures import BoundingBox, Instance, SegmentationMask
from toolbox.Structures.Keypoints import COCOKeypoints


class Detectron2:
    """Predict images using detectron2 models.

    Attributes:
        dataset_classes (List[str]): List of class labels.
    """

    def __init__(self, model_config: Path,
                 model_weights: Optional[str] = None,
                 confidence_threshold: Optional[float] = 0.5,
                 use_cuda: bool = False):
        """Create and load a detectron2 model.

        Args:
            model_config (Path): Path to the detectron2 configuration YAML.
            model_weights (Optional[str], optional): Optional path or URL to
                the model weights file. Defaults to None.
            confidence_threshold (Optional[float], optional): Minimum
                detection confidence of the instances. Defaults to 0.5.
            use_cuda (bool, optional): Execute the model on a CUDA device.
                Defaults to False.
        """
        self._setup_cfg(model_config, model_weights, use_cuda)
        self._predictor = DefaultPredictor(self.cfg)
        self._conf_thr = confidence_threshold

        self._dataset_metadata = MetadataCatalog.get(
            self.cfg.DATASETS.TEST[0]
            if len(self.cfg.DATASETS.TEST)
            else "__unused"
        )
        self.dataset_classes = self._dataset_metadata.get(
            "thing_classes", None)

    def predict(self, image: np.ndarray) -> List[Instance]:
        """Predict an image.

        Args:
            image (np.ndarray): A BGR uint8 image of shape (H, W, 3).

        Returns:
            List[Instance]: List of instances, depending on the model it will
                have the following fields:
                - confidence (float): The confidence level of the detection.
                - label (str): Predicted label string.
                - label_id (int): Id of the predicted label.
                - bounding_box (BoundingBox): A bounding box of the object.
                - mask (SegmentationMask): A segmentation mask of the object.
                - keypoints (COCOKeypoints): Person keypoints.
        """
        predictions = self._predictor(image)

        boxes = None
        scores = None
        labels_id = None
        labels = None
        keypoints = None
        masks = None
        ret_instances = []

        if "instances" in predictions:

            # Convert tensors to numpy arrays
            det_instances = predictions["instances"]
            if det_instances.has("scores"):
                scores = det_instances.scores.cpu().numpy()
            if det_instances.has("pred_boxes"):
                boxes = det_instances.pred_boxes.tensor.cpu().numpy()
            if det_instances.has("pred_classes"):
                labels_id = det_instances.pred_classes.tolist()
                labels = self._create_text_labels(labels_id)
            if det_instances.has("pred_keypoints"):
                keypoints = det_instances.pred_keypoints.cpu().numpy()
            if det_instances.has("pred_masks"):
                masks = np.asarray(det_instances.pred_masks.cpu().numpy())

            # Parse the detection results
            for i in range(len(det_instances)):
                ins = Instance()

                # Confidence
                if scores is not None:
                    if scores[i] < self._conf_thr:
                        continue
                    ins.set("confidence", scores[i])

                # Classification
                if labels_id is not None:
                    ins.set("label_id", labels_id[i])
                    ins.set("label", labels[i])

                # Bounding boxes
                if boxes is not None:
                    ins.set(
                        "bounding_box",
                        BoundingBox.from_absolute(
                            boxes[i][0],
                            boxes[i][1],
                            boxes[i][2],
                            boxes[i][3],
                            image_width=image.shape[1],
                            image_height=image.shape[0]
                        )
                    )

                # Segmentation mask
                if masks is not None:
                    ins.set("mask", SegmentationMask(masks[i]))

                # Keypoints
                if keypoints is not None:
                    ins.set("keypoints", COCOKeypoints.from_absolute_keypoints(
                        keypoints[i],
                        image.shape[1],
                        image.shape[0]
                    ))

                ret_instances.append(ins)

        return ret_instances

    def _create_text_labels(self, classes: List[int]) -> List[str]:
        """Convert a list of class IDs to a list of class names using the
        dataset metadata. If the class names are not available, a string of the
        IDs are returned.

        Args:
            classes (List[int]): A list of classes IDs

        Returns:
            List[str]: A list of class names.
        """
        if self.dataset_classes is not None and len(self.dataset_classes) > 0:
            return [self.dataset_classes[i] for i in classes]
        else:
            return [str(i) for i in classes]

    def _setup_cfg(self, config_path: Path,
                   model_weights: Optional[str] = None, use_cuda: bool = False):
        """Create the model cfg.

        Args:
            config_path (Path): Path to the detectron2 configuration YAML.
            model_weights (Optional[str], optional): Optional path or URL to
                the model weights file. Defaults to None.
            use_cuda (bool, optional): Execute the model on a CUDA device.
                Defaults to False.
        """
        self.cfg = get_cfg()
        self.cfg.merge_from_file(str(config_path))
        if model_weights is not None:
            self.cfg.MODEL.WEIGHTS = str(model_weights)
        if use_cuda:
            self.cfg.MODEL.DEVICE = "cuda"
        else:
            self.cfg.MODEL.DEVICE = "cpu"
        self.cfg.freeze()
