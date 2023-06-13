import argparse
import json
import secrets
import urllib
from pathlib import Path
from typing import List, Union

import aiofiles
import cv2
import fastapi
import uvicorn
from fastapi import (BackgroundTasks, Body, FastAPI, File, HTTPException,
                     UploadFile, status)
from fastapi.responses import FileResponse
from fastapi_utils.tasks import repeat_every
from starlette.middleware.cors import CORSMiddleware

from toolbox import DataModels, Structures
from toolbox.Context import ContextCli
from toolbox.Projects.ImageStorage.ContentSizeLimitMiddleware import \
    ContentSizeLimitMiddleware
from toolbox.Projects.ImageStorage.Storage import Storage
from toolbox.utils.config_utils import parse_config
from toolbox.utils.utils import (float_or_none, get_logger, get_version,
                                 hash_str, urljoin)
from toolbox.Visualization import DataModelVisualizer

logger = get_logger("toolbox.ImageStorage")


class ImageStorage:
    """API to upload and download images, keeping a reference to the file
    in a context broker. It also allows the creation of data models
    visualization images.
    """

    VERSION = get_version()
    TITLE = "Image Storage API"

    def __init__(self, config: dict):
        """Start the api server.

        Args:
            config (dict): Configuration dict.
        """
        # Parse config
        self._port = int(config["api"]["port"])
        self._host = config["api"]["host"]
        self._external_url = config["api"]["external_url"]
        self._ngsild_urn = str(config["api"]["ngsild_urn"])
        self._allowed_origins = config["api"]["allowed_origins"]
        self._allowed_mimes = config["api"]["allowed_mime"]
        self._cleanup_on_end = config["api"]["cleanup_on_end"]
        self._max_upload_size = float_or_none(config["api"]["max_upload_size"])
        self._max_file_time = float_or_none(config["api"]["max_file_time"])
        self._update_time = float_or_none(config["api"]["update_time"])
        self._allow_upload = config["api"]["allow_uploads"]
        self._allow_visualize = config["api"]["allow_entity_visualization"]
        self._max_n_entities_vis = float_or_none(
            config["api"]["max_entities_visualize"])

        # Create the storage object
        self._storage = Storage(config)
        self._storage.initialize()
        self._storage.check_dir_limits()

        # Create the context consumer
        if self._allow_visualize:
            self.context_cli = ContextCli(**config["context_broker"])
            self._visualizer = DataModelVisualizer(
                config.get("visualization", {}))

        # Run the API
        self._api = self._server()
        uvicorn.run(self._api, host=self._host, port=self._port)
        self._end()

    def _end(self):
        """Method called at the end of the execution.
        """
        if self._cleanup_on_end:
            self._storage.delete_all()

    async def _start_check_files_time(self):
        """Run infinite loop to check the maximum file time.
        """
        @repeat_every(seconds=self._update_time)
        def run():
            self._storage.check_files_time()
        logger.info(f"Checking file time every {self._update_time} seconds")
        await run()

    def _set_routes(self, app: FastAPI) -> FastAPI:
        """Create the API routes.

        Args:
            app (FastAPI).

        Returns:
            FastAPI.
        """
        @app.get(
            "/{image_id}",
            response_description="An image file",
            response_class=FileResponse,
            responses={
                404: {"description": "File not found"}
            }
        )
        async def get(image_id: str = fastapi.Path(description="Image id")):
            """Get an image by its id.
            """
            if image_id not in self._storage:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    f"File not found",
                )
            return FileResponse(self._storage[image_id])

        if self._allow_upload:
            @app.post(
                "/",
                response_description="The id of the uploaded image",
                responses={
                    415: {"description": "Unsupported Media Type"},
                    413: {"description": "Content Too Large"}
                }
            )
            async def post(
                background_tasks: BackgroundTasks,
                file: UploadFile = File(description="An image file"),
                source: str = Body("", description="Source of the image"),
                purpose: str = Body("", description="Purpose of the image")
            ) -> str:
                """Post an image.
                """
                # Check the storage dir limits at the end of execution
                background_tasks.add_task(self._storage.check_dir_limits)
                # Check the file type
                if file.content_type not in self._allowed_mimes:
                    raise HTTPException(
                        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        f"Unsupported media type: {file.content_type}. "
                        f"It must be one of {self._allowed_mimes}",
                    )
                # Set the image token
                token = secrets.token_urlsafe()
                entity_id = self._ngsild_urn.format(token)
                extension = file.filename.rsplit(".", maxsplit=1)[-1]
                out_path = self._storage.get_file_path(
                    f"{entity_id}.{extension}"
                )
                # Write the image to disk
                async with aiofiles.open(out_path, 'wb') as out_file:
                    while content := await file.read(1024):
                        await out_file.write(content)
                # Check the image integrity
                try:
                    img = cv2.imread(str(out_path), cv2.IMREAD_UNCHANGED)
                    assert img is not None and img.ndim > 1
                except:
                    out_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status.HTTP_422_UNPROCESSABLE_ENTITY,
                        f"Error reading image",
                    )
                # Create the image entity
                url = urljoin(self._external_url,
                              urllib.parse.quote(entity_id))
                data_model = DataModels.Image(
                    id=entity_id,
                    width=img.shape[1],
                    height=img.shape[0],
                    path=str(out_path),
                    url=url,
                    source=source,
                    purpose=purpose
                )
                self._storage.add_file(out_path, data_model)
                return entity_id

        if self._allow_visualize:
            # TODO: also use image url (check is not from the same api)
            @app.post(
                "/visualize",
                response_description="The generated image and its token",
                responses={
                    404: {"description": "Entity not found"},
                }
            )
            async def visualize(
                background_tasks: BackgroundTasks,
                entity_ids: Union[List[str], str] = Body(
                    description="An entity id or a list of ids to visualize. "
                    "All entities must have the same source image."),
                params: dict = Body({},
                                    description="Optional visualization params")
            ) -> str:
                """Visualize the data of one or more entities.
                """
                # Check the storage dir limits at the end of execution
                background_tasks.add_task(self._storage.check_dir_limits)

                if isinstance(entity_ids, str):
                    entity_ids = [entity_ids]
                else:
                    entity_ids.sort()

                if self._max_n_entities_vis is not None and \
                        len(entity_ids) > self._max_n_entities_vis:
                    raise HTTPException(
                        status.HTTP_422_UNPROCESSABLE_ENTITY,
                        f"Too many entities {len(entity_ids)}. "
                        f"Maximum is {self._max_n_entities_vis}"
                    )

                # Get the entities
                entities_str = ""
                image_id = ""
                dms = []
                for e_id in entity_ids:
                    try:
                        dm = self.context_cli.get_entity(e_id)
                        if dm is None:
                            logger.error(f"Entity not found: {e_id}")
                            raise HTTPException(
                                status.HTTP_404_NOT_FOUND,
                                f"Entity not found: {e_id}",
                            )
                    except KeyError as e:
                        logger.error(e, exc_info=True)
                        raise HTTPException(
                            status.HTTP_422_UNPROCESSABLE_ENTITY,
                            f"Unprocessable entity type: {e_id}"
                        )
                    entities_str += repr(dm)
                    dms.append(dm)
                    if image_id and dm.image != image_id:
                        raise HTTPException(
                            status.HTTP_422_UNPROCESSABLE_ENTITY,
                            f"Found entities with different images "
                            f"({dm.image} != {image_id})",
                        )
                    image_id = dm.image

                # Set the token
                params_str = json.dumps(
                    params, sort_keys=True, ensure_ascii=True
                ) + json.dumps(
                    self._visualizer.config, sort_keys=True, ensure_ascii=True
                )
                token = hash_str(entities_str+params_str)
                if token in self._storage:
                    return token

                # Get the image
                try:
                    image_dm = self.context_cli.get_entity(image_id)
                    if image_dm is None:
                        logger.error(f"Image not found: {image_id}")
                        raise HTTPException(
                            status.HTTP_404_NOT_FOUND,
                            f"Image not found: {image_id}",
                        )
                except KeyError as e:
                    logger.error(e, exc_info=True)
                    raise HTTPException(
                        status.HTTP_422_UNPROCESSABLE_ENTITY,
                        f"Unprocessable entity type: {image_id}"
                    )
                if not isinstance(image_dm, DataModels.Image):
                    logger.error(f"Image expected. Got {type(image_dm)}")
                    raise HTTPException(
                        status.HTTP_422_UNPROCESSABLE_ENTITY,
                        f"Entity {image_id} is not an image"
                    )
                try:
                    image = Structures.Image.from_path(Path(image_dm.path))
                except FileNotFoundError as e:
                    logger.error(e, exc_info=True)
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        f"Image not found: {image_id}"
                    )

                # Visualize the data models
                vis_image = self._visualizer.visualize_data_models(
                    image.image,
                    dms,
                    params
                )

                # Set the output path and save the image
                out_path = self._storage.get_file_path(f"{token}.jpg")
                cv2.imwrite(str(out_path), vis_image)
                self._storage.add_file(out_path, key=token)
                return token

        return app

    def _server(self) -> FastAPI:
        """Create the FastAPI app.

        Returns:
            FastAPI
        """
        app = FastAPI(
            title=self.TITLE,
            version=self.VERSION,
        )
        if self._allowed_origins:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=self._allowed_origins
            )
        if self._max_upload_size is not None:
            app.add_middleware(
                ContentSizeLimitMiddleware,
                max_content_size=self._max_upload_size
            )
        if self._max_file_time is not None:
            app.add_event_handler("startup", self._start_check_files_time)
        app = self._set_routes(app)
        return app


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--config",
        help="Path to the configuration YAML (default: 'config.yaml')",
        type=Path,
        default="config.yaml"
    )
    ap.add_argument(
        "--log-level",
        help="Log level",
        choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
        default="INFO"
    )
    args = ap.parse_args()
    logger.setLevel(args.log_level)
    config = parse_config(args.config)
    ImageStorage(config)


if __name__ == "__main__":
    main()
