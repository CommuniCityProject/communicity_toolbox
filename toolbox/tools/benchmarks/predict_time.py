from typing import List, Optional
import argparse
import time
from pathlib import Path

import numpy as np
import cv2
from tqdm import tqdm
from mean_average_precision import MetricBuilder

from toolbox.Models import model_catalog
from toolbox.utils.config_utils import parse_config


def get_images_list(images_path: Path) -> List[Path]:
    """Get the path of all the images on a directory recursively.

    Args:
        images_path (Path): Root images path.

    Returns:
        List[Path]: List with all the images on a directory.
    """
    paths = []
    for p in images_path.iterdir():
        if p.is_dir():
            paths += get_images_list(p)
        else:
            paths.append(p)
    return paths


def main(images_path: Path, config_path: Path, model_key: Optional[str] = None):
    # Load the model config
    config = parse_config(config_path)

    # Create the model
    if model_key is not None:
        config = config[model_key]
    model_name = config["model_name"]
    model_params = config["params"]
    model = model_catalog[model_name](**model_params)

    # Get the images paths
    paths = get_images_list(images_path)

    # Predict the images
    times = []
    try:
        for img_path in tqdm(paths):
            img = cv2.imread(str(img_path))
            ti = time.time()
            model.predict(img)
            tf = time.time()
            times.append(tf-ti)
    except KeyboardInterrupt:
        # Show partial results if ctrl+c
        pass

    times = np.array(times)

    # Print times
    print(f"Time (s): Min: {times.min()} Mean: {times.mean()}, "
          f"Max: {times.max()}")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Compute the mean inference time "
                                             "of a model.")
    ap.add_argument(
        "-i",
        "--images-path",
        help="Root path to the images",
        type=Path,
        required=True
    )
    ap.add_argument(
        "-c",
        "--config",
        help="Path to a configuration YAML file with the parameters and model "
             "name.",
        type=Path,
        required=True
    )
    ap.add_argument(
        "-k",
        "--model-key",
        help="Optional key on the configuration YAML containing the model's "
            "parameters",
    )
    args = ap.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args.images_path, args.config, args.model_key)
