import argparse
import warnings
from pathlib import Path
from typing import Optional

from tqdm import tqdm

from toolbox.Projects.FaceRecognition import FaceRecognition
from toolbox.Structures import Image
from toolbox.utils.config_utils import parse_config


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Create a face recognition dataset from a set of images. "
        "There should be one image for each person. The filename will be used "
        "as its name or id (';' are replaced with ':'). Images must contain "
        "only one face."
    )
    ap.add_argument(
        "-c",
        "--config",
        help="Path to the configuration YAML (default 'config.yaml')",
        type=Path,
        default="config.yaml"
    )
    ap.add_argument(
        "-i",
        "--images",
        help="Path to an image or images folder. The filename of each image "
        "will be its name or id. ';' are replaced with ':'",
        required=True,
        type=Path
    )
    ap.add_argument(
        "-d",
        "--dataset",
        help="Path to a dataset pickle file, to load and combine with the "
        "current images",
        default=None,
        type=Path
    )
    ap.add_argument(
        "-o",
        "--output",
        help="Output pickle file to save the dataset",
        required=True
    )
    args = ap.parse_args()
    return args


def main(config_path: Path, image_path: Path, dataset_path: Optional[Path],
         output_path: Path):

    if image_path.is_file():
        images_path = [image_path]
    else:
        images_path = list(image_path.iterdir())

    config = parse_config(config_path)
    config["api"]

    recognition = FaceRecognition(config, do_extraction=True)

    if dataset_path is not None:
        recognition.load_dataset(dataset_path)

    pbar = tqdm(images_path, unit="img")
    for image_path in pbar:
        pbar.set_description(str(image_path))
        dms = recognition.predict(Image(image_path))
        if len(dms) > 1:
            warnings.warn(
                f"\nDetected more than one face on {image_path} ({len(dms)})"
            )
        recognition.register_features(
            dms[0], image_path.stem.replace(";", ":"))

    recognition.save_dataset(output_path)


if __name__ == "__main__":
    args = parse_args()
    main(
        config_path=args.config,
        image_path=args.images,
        dataset_path=args.dataset,
        output_path=args.output
    )
