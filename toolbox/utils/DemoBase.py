import argparse
import json
import os
from pathlib import Path
from typing import List, Optional, Type, Union

import cv2
import numpy as np

from toolbox.Context import ContextCli, entity_parser
from toolbox.DataModels import BaseModel
from toolbox.Structures import Image
from toolbox.utils.config_utils import parse_config
from toolbox.utils.simple_http_server import create_http_server
from toolbox.utils.utils import is_url
from toolbox.Visualization import DataModelVisualizer


class DemoBase:
    """Base class to implement a demo application for the toolbox projects.

    Methods to be implemented:
        _load_model(config, task)
        _process_image(image)
    """

    def __init__(self):
        """Initialize the demo.
        """
        pass

    def _get_parser_parent(self) -> argparse.ArgumentParser:
        """Create the parent parser with the common arguments shared between
        the different tasks.

        Returns:
            argparse.ArgumentParser
        """
        parent_ap = argparse.ArgumentParser()
        parent_ap.add_argument(
            "-c",
            "--config",
            help="Path to the configuration YAML (default 'config.yaml')",
            type=Path,
            default="config.yaml"
        )
        return parent_ap

    def _get_parser_local(self, sub_parser: argparse.ArgumentParser
                          ) -> argparse.ArgumentParser:
        """Create the local-task parser.

        Args:
            sub_parser (argparse.ArgumentParser)

        Returns:
            argparse.ArgumentParser
        """
        local_ap = sub_parser.add_parser(
            "local",
            help="Run the project locally"
        )
        local_ap.add_argument(
            "-i",
            "--image",
            help="Path or URL to an image or folder with images",
            required=True
        )
        local_ap.add_argument(
            "-o",
            "--output",
            help="Optional output image file path when running a single "
            "image or an output folder when running on multiple images",
            type=Path,
            default=None
        )
        return local_ap

    def _get_parser_producer(self, sub_parser: argparse.ArgumentParser
                             ) -> argparse.ArgumentParser:
        """Create the producer-task parser.

        Args:
            sub_parser (argparse.ArgumentParser)

        Returns:
            argparse.ArgumentParser
        """
        prod_ap = sub_parser.add_parser(
            "producer",
            help=""""Run the project on images and upload the results to a 
            context broker"""
        )
        prod_ap.add_argument(
            "-i",
            "--image",
            help="Path or URL to an image or folder with images",
            required=True
        )
        return prod_ap

    def _get_parser_consumer(self, sub_parser: argparse.ArgumentParser
                             ) -> argparse.ArgumentParser:
        """Create the consumer-task parser.

        Args:
            sub_parser (argparse.ArgumentParser)

        Returns:
            argparse.ArgumentParser
        """
        cons_ap = sub_parser.add_parser(
            "consumer",
            help="Retrieve and parse entities from a context broker"
        )
        cons_ap.add_argument(
            "-i",
            "--id",
            help="Optional entity ID",
            default=None
        )
        cons_ap.add_argument(
            "-s",
            "--subscribe",
            action="store_true",
            help="Subscribe to the context broker with the subscriptions "
            "in the config",
        )
        cons_ap.add_argument(
            "--post-to-broker",
            action="store_true",
            help="Post the consumed entities to the context broker",
        )
        return cons_ap

    def _get_parser_visualize(self, sub_parser: argparse.ArgumentParser
                              ) -> argparse.ArgumentParser:
        """Create the visualize-task parser.

        Args:
            sub_parser (argparse.ArgumentParser)

        Returns:
            argparse.ArgumentParser
        """
        vis_ap = sub_parser.add_parser(
            "visualize",
            help="Visualize an entity from the context broker"
        )
        vis_ap.add_argument(
            "-i",
            "--id",
            help="Entity ID",
            required=True
        )
        vis_ap.add_argument(
            "--image",
            help="Optional image file where draw the retrieved entity. "
            "If not set, it will try to get the image by its ID",
            default=None
        )
        vis_ap.add_argument(
            "-o",
            "--output",
            help="Output image file path",
            type=Path,
            required=True
        )
        return vis_ap

    def _get_args(self) -> argparse.Namespace:
        """Get the parsed arguments.

        Returns:
            argparse.ArgumentParser
        """
        parser = self._get_parser_parent()
        sub_parser = parser.add_subparsers(
            title="task",
            dest="task",
            required=True
        )
        local_ap = self._get_parser_local(sub_parser)
        prod_ap = self._get_parser_producer(sub_parser)
        cons_ap = self._get_parser_consumer(sub_parser)
        vis_ap = self._get_parser_visualize(sub_parser)
        return parser.parse_args()

    def run(self):
        """Run the demo.
        """
        args = self._get_args()
        config = parse_config(args.config)
        self._load_model(config, args.task)

        self.visualizer = DataModelVisualizer(config.get("visualization", {}))

        if args.task != "local":
            self.context_cli = ContextCli(**config["context_broker"])

        if args.task == "local":
            self._run_local(args.image, args.output)
        elif args.task == "producer":
            self._run_producer(args.image)
        elif args.task == "consumer":
            self._run_consumer(
                args.id, config, args.subscribe, args.post_to_broker)
        elif args.task == "visualize":
            self._run_visualize(args.id, args.output, args.image)

    def _load_model(self, config: dict, task: str):
        """Load the project models.

        Args:
            config (dict): The parsed config dict.
            task (str): The task name ["local" | "producer" | "consumer"]

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    def _process_image(self, image: Image) -> List[Type[BaseModel]]:
        """Run the project on a single image.

        Args:
            image (Image): An image object.

        Raises:
            NotImplementedError

        Returns:
            List[Type[BaseModel]]: A list of data model objects.
        """
        raise NotImplementedError

    def _run_local(self, image_path: str, output: Optional[Path] = None):
        """Run the project locally on images.

        Args:
            image_path (str): Path or URL to an image or folder with images.
            output (Optional[Path], optional): Output image or folder path.
                Defaults to None.
        """
        if image_path == output:
            raise FileExistsError("Output path can not be the same as "
                                  f"the input ({image_path}) ({output})")
        if not is_url(image_path) and os.path.isdir(image_path):
            image_paths = list(Path(image_path).iterdir())
            is_dir = True
        else:
            image_paths = [image_path]
            is_dir = False

        for path in image_paths:
            image = Image(path)
            data_models = self._process_image(image)
            self._print_data_models(data_models)
            if output is not None:
                out_image = self.visualizer.visualize_data_models(
                    image.image, data_models)
                if is_dir:
                    output.mkdir(parents=True, exist_ok=True)
                    cv2.imwrite(str(output / path.name), out_image)
                else:
                    output.parent.mkdir(parents=True, exist_ok=True)
                    cv2.imwrite(str(output), out_image)

    def _run_producer(self, image_path: str):
        """Run the project on images, upload the results to a context broker
        and print the generated entities.

        Args:
            image_path (Path): Path or URL to an image or folder with images.
        """
        if not is_url(image_path) and os.path.isdir(image_path):
            image_paths = list(Path(image_path).iterdir())
        else:
            image_paths = [image_path]
        for path in image_paths:
            for dm in self._process_image(Image(path)):
                entity = self.context_cli.post_data_model(dm)
                print(json.dumps(entity, indent=4))

    def _consume_data_model(self, data_model: Type[BaseModel]
                            ) -> List[Type[BaseModel]]:
        """Process the retrieved data model from a context context broker.

        Args:
            data_model (Type[BaseModel]): A data model.

        Returns:
            List[Type[BaseModel]]: List of generated data model.
        """
        return data_model

    def _run_consumer(self, e_id: Optional[str], config: dict,
                      subscribe: bool = False, post_to_broker: bool = False):
        """Retrieve and parse entities from a context broker.

        Args:
            e_id (Optional[str]): The ID of an entity.
            config (dict): The configuration dict.
            subscribe (bool, optional): Subscribe to a context broker to
                process every new entity. Defaults to False.
        """
        if e_id is not None:
            data_model = self.context_cli.get_entity(e_id)
            assert data_model is not None
            dms = self._consume_data_model(data_model)
            self._print_data_models(dms)
            if post_to_broker:
                [self.context_cli.update_data_model(dm, create=True)
                    for dm in dms]

        if subscribe:
            def on_notify(path: str, c_type: str, data: str):
                entity_dict = json.loads(data)
                for data in entity_dict["data"]:
                    data_model = entity_parser.json_to_data_model(data)
                    dms = self._consume_data_model(data_model)
                    self._print_data_models(dms)
                    if post_to_broker:
                        [self.context_cli.update_data_model(dm, create=True)
                            for dm in dms]
                return ""
            for sub in config.get("subscriptions", []):
                self.context_cli.subscribe(
                    entity_type=sub["entity_type"],
                    watched_attributes=sub.get("watched_attributes", []),
                    query=sub.get("query", "")
                )
            try:
                print(f"Notifications endpoint: "
                      f"{self.context_cli.notification_uri}")
                create_http_server(
                    port=config["api"]["port"],
                    get_callback=None,
                    post_callback=on_notify
                )
            except KeyboardInterrupt:
                pass
            except Exception as e:
                self.context_cli.unsubscribe_all()
                raise e
            self.context_cli.unsubscribe_all()

    def _run_visualize(self, e_id: str, output: Path,
                       image_path: Optional[Path] = None):
        """Visualize one entity from a context broker.

        Args:
            e_id (str): The ID of an entity.
            output (Path): The output image file path.
        """
        data_model = self.context_cli.get_entity(e_id)
        assert data_model is not None
        self._print_data_models(data_model)

        image = None
        if image_path is not None:
            image = cv2.imread(str(image_path))
        elif data_model.image:
            img_dm = self.context_cli.get_entity(data_model.image)
            try:
                if img_dm.url:
                    image = Image(img_dm.url).image
            except Exception as e:
                print(f"Error getting the image: {data_model.image} {e}")
        if image is None:
            image = np.zeros((2000, 2000, 3), dtype="uint8")

        out_image = self.visualizer.visualize_data_models(
            image, data_model)
        output.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output), out_image)

    def _print_data_models(self,
                           data_models: Union[List[Type[BaseModel]],
                           Type[BaseModel]]):
        """Print one or more data models.

        Args:
            data_models (Tuple[List[Type[BaseModel]], Type[BaseModel]])
        """
        if not isinstance(data_models, (tuple, list)):
            print(data_models.pretty())
        else:
            [print(dm.pretty()) for dm in data_models]
