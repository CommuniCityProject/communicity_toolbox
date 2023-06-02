from typing import Dict, List
import argparse
import time
from pathlib import Path

import numpy as np
import cv2
from tqdm import tqdm
from mean_average_precision import MetricBuilder

from toolbox.Models import model_catalog
from toolbox.utils.config_utils import parse_config


def get_images_boxes(wider_images: Path, wider_gt: Path
                     ) -> Dict[Path, List[list]]:
    gt_lines = wider_gt.read_text().splitlines()
    bounding_boxes: Dict[Path, List[list]] = {}
    i = 0
    while i < len(gt_lines):
        img_path = gt_lines[i]
        i += 1
        img_path = wider_images / img_path
        bounding_boxes[img_path] = []
        bb_count = int(gt_lines[i])
        i += 1
        for _ in range(bb_count):
            bb_str = gt_lines[i].split(" ")
            i += 1

            if "1" in bb_str[4:] or "2" in bb_str[4:]:
                continue

            xmin = int(bb_str[0])
            ymin = int(bb_str[1])
            w = int(bb_str[2])
            h = int(bb_str[3])
            xmax = xmin + w
            ymax = ymin + h
            # [xmin, ymin, xmax, ymax, class_id, difficult, crowd]
            bounding_boxes[img_path].append([xmin, ymin, xmax, ymax, 0, 0, 0])
        bounding_boxes[img_path] = np.array(bounding_boxes[img_path])
    return bounding_boxes


def main(wider_images: Path, wider_gt: Path, config_path: Path):
    # Load the model config
    config = parse_config(config_path)

    # Create the model
    model_name = config["face_detector"]["model_name"]
    model_params = config["face_detector"]["params"]
    model = model_catalog[model_name](**model_params)

    # Create the metric function (mAP)
    metric_fn = MetricBuilder.build_evaluation_metric(
        "map_2d",
        async_mode=False,
        num_classes=1
    )

    # Parse the dataset
    images_boxes = get_images_boxes(wider_images, wider_gt)

    # Predict the images
    times = []
    for img_path, gt_boxes in tqdm(images_boxes.items()):
        if not gt_boxes.any():
            continue
        img = cv2.imread(str(img_path))
        ti = time.time()
        instances = model.predict(img)
        tf = time.time()
        times.append(tf-ti)

        # [xmin, ymin, xmax, ymax, class_id, confidence]
        pred_boxes = [
            np.append(
                i.bounding_box.get_xyxy(
                    absolute=True,
                    image_width=img.shape[1],
                    image_height=img.shape[0]
                ),
                [0, i.confidence]
            )
            for i in instances
        ]
        pred_boxes = np.array(pred_boxes)
        metric_fn.add(pred_boxes, gt_boxes)

    times = np.array(times)

    # Compute PASCAL VOC metric
    voc_map = metric_fn.value(
        iou_thresholds=0.5,
        recall_thresholds=np.arange(0., 1.1, 0.1)
    )["mAP"]
    
    # Compute PASCAL VOC metric at the all points
    voc_map_all = metric_fn.value(iou_thresholds=0.5)["mAP"]
    
    # Compute metric COCO metric
    coco_map = metric_fn.value(
        iou_thresholds=np.arange(0.5, 1.0, 0.05),
        recall_thresholds=np.arange(0., 1.01, 0.01),
        mpolicy="soft"
    )["mAP"]

    print(f"VOC PASCAL mAP: {voc_map}")
    print(f"VOC PASCAL mAP in all points: {voc_map_all}")
    print(f"COCO mAP: {coco_map}")

    # Print times
    print(f"Time (s): Min: {times.min()} Mean: {times.mean()}, "
          f"Max: {times.max()}")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Evaluate the mean average "
                                 "precision (mAP) and mean inference time "
                                 "over the WIDER dataset of a face detector "
                                 "model.")
    ap.add_argument(
        "-i",
        "--wider-images",
        help="Path to the WIDER val images",
        type=Path,
        required=True
    )
    ap.add_argument(
        "-g",
        "--wider-gt",
        help="Path to the WIDER val ground-truth file",
        type=Path,
        required=True
    )
    ap.add_argument(
        "-c",
        "--config",
        help="Path to a configuration YAML file with the parameters and model "
             "name under a 'face_detector' field.",
        type=Path,
        required=True
    )
    args = ap.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args.wider_images, args.wider_gt, args.config)
