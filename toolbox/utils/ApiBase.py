import argparse
import logging
from pathlib import Path
from typing import Any, List, Optional, Type, Union

import uvicorn
from fastapi import (Body, FastAPI, HTTPException, Query, Request, Response,
                     status)
from fastapi.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from toolbox import DataModels, Structures
from toolbox.Context import ContextCli, entity_parser
from toolbox.DataModels import BaseModel, Notification
from toolbox.utils.config_utils import parse_config
from toolbox.utils.utils import get_logger, get_version

logger = get_logger("toolbox.Api")


class ApiBase:
    """Base class to implement an API for the toolbox projects.

    Attributes to override:
        VERSION (str): The version of the API.
        TITLE (str): The title of the API.

    Attributes:
        host (str): The bind host.
        port (int): The bind port.
        allowed_origins (List[str]): List of origins that should be permitted
            to make cross-origin requests.
        local_image_storage (bool): If the images are stored locally and can
            be accessed by their path.
        context_cli (ContextCli): The ContextCli.
        config (dict): The config of the API.
        base_dm (Optional[Type[BaseModel]]): Data model class that will be send.

    Methods to be implemented:
        _predict_entity(data_model, post_to_broker) -> List[Type[BaseModel]]
    """

    VERSION = get_version()
    TITLE = "BASE API"

    def __init__(self, base_dm: Optional[Type[BaseModel]] = None):
        """Initialize the API.

        Args:
            base_dm (Optional[Type, optional): Data model class that will
                be send. Defaults to None.
        """
        self.host: str
        self.port: int
        self.allowed_origins: List[str]
        self.local_image_storage: bool
        self.context_cli: ContextCli
        self.config: dict
        self.base_dm = base_dm

    def _parse_args(self) -> argparse.Namespace:
        """Parse the command-line arguments.

        Returns:
            argparse.Namespace: The parsed command-line arguments.
        """
        ap = argparse.ArgumentParser()
        ap.add_argument(
            "--config",
            help="Path to the configuration yaml (default: 'config.yaml')",
            type=Path,
            default="config.yaml"
        )
        ap.add_argument(
            "--log-level",
            help="Log level (default: INFO)",
            choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
            default="INFO"
        )
        args = ap.parse_args()
        return args

    def _set_subscriptions(self):
        """Create the subscriptions from the config.
        """
        for sub in self.config.get("subscriptions", []):
            self.context_cli.subscribe(
                entity_type=sub["entity_type"],
                watched_attributes=sub.get("watched_attributes", []),
                query=sub.get("query", "")
            )

    def _initialize(self, args: argparse.Namespace):
        """Initialize the api.

        Args:
            args (argparse.Namespace): The parsed command-line arguments.
        """
        self.config = parse_config(args.config)
        self.port = self.config["api"]["port"]
        self.host = self.config["api"]["host"]
        self.allowed_origins = self.config["api"]["allowed_origins"]
        self.local_image_storage = self.config["api"]["local_image_storage"]
        self.context_cli = ContextCli(**self.config["context_broker"])
        logging.getLogger("toolbox").setLevel(args.log_level)
        self._set_subscriptions()

    def _end(self):
        """Method called at the end of the execution
        """
        self.context_cli.unsubscribe_all()

    def _process_notified_models(self, data_models: List[Type[BaseModel]],
                                 subscription_id: str):
        """Process the notified data models from a subscription.

        Args:
            data_models (List[Type[BaseModel]]): A list of data model objects.
            subscription_id (str): The id of the subscription that triggered
                the notification.
        """
        if subscription_id not in self.context_cli.subscription_ids:
            logger.warning(f"Received a notification from a foreign "
                           f"subscription: {subscription_id}")
        for dm in data_models:
            try:
                self._predict_entity(dm, post_to_broker=True)
            except HTTPException as e:
                logger.error(str(e))

    def _get_image_from_dm(self, image_dm: DataModels.Image) -> Structures.Image:
        """Get an Image structure from an Image data model.

        Args:
            image_dm (DataModels.Image): The image data model.

        Raises:
            HTTPException

        Returns:
            Structures.Image: An Image object.
        """
        if self.local_image_storage:
            image = Structures.Image(path=image_dm.path)
        else:
            image = Structures.Image(path=image_dm.url)
        image.id = image_dm.id
        try:
            image.image
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Unable to load the image '{image.id}'"
            )
        return image

    def _get_image_by_id(self, image_id: str) -> Union[Structures.Image, None]:
        """Get an image from an image entity by its id.

        Args:
            image_id (str): The id of an image entity.

        Raises:
            HTTPException

        Returns:
            Union[Structures.Image, None]: An Image object.
        """
        try:
            image_dm = self.context_cli.get_entity(image_id)
            if image_dm is None:
                logger.error(f"Image not found: {image_id}")
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    f"Image not found: {image_id}"
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
        return self._get_image_from_dm(image_dm)

    def _set_route_get_root(self, app: FastAPI) -> FastAPI:
        """Set the get-root route.

        Args:
            app (FastAPI)

        Returns:
            FastAPI
        """
        @app.get("/")
        def get_root():
            return {
                "title": self.TITLE,
                "version": self.VERSION
            }
        return app

    def _set_route_post_notification(self, app: FastAPI) -> FastAPI:
        """Set the post-notification route. 

        Args:
            app (FastAPI)

        Returns:
            FastAPI
        """
        @app.post("/ngsi-ld/v1/notify", status_code=204)
        def notify(
            subscriptionId: str = Query(description="The subscription id "
                                        "that triggered the notification"),
            notification: Notification = Body(description="The notification"
                                              " data")
        ):
            """Notify the activation of a subscription.
            """
            data_models = [
                entity_parser.json_to_data_model(entity)
                for entity in notification.data
            ]
            self._process_notified_models(data_models, subscriptionId)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return app

    def _predict_entity(self, data_model: Type[BaseModel],
                        post_to_broker: bool) -> List[Type[BaseModel]]:
        """Predict a data model.

        Args:
            data_model (Type[BaseModel]): The data model to predict.
            post_to_broker (bool): Post the predicted data models to the
                context broker.

        Raises:
            NotImplementedError

        Returns:
            List[Type[BaseModel]]: The predicted data models.
        """
        raise NotImplementedError

    def _get_default_ok_response(self) -> dict:
        return {
            "content": {
                "application/json": {
                    "model": self.base_dm()
                },
                "application/ld+json": {
                    "example": entity_parser.data_model_to_json(self.base_dm())
                }
            }
        }

    def _return_data_model_for_accept(
        self,
        data_models: Union[List[Type[DataModels.BaseModel]], Type[DataModels.BaseModel]],
        accept: str
    ) -> Any:
        if accept == "application/ld+json":
            if isinstance(data_models, (list, tuple)):
                ret = [entity_parser.data_model_to_json(dm)
                       for dm in data_models]
            else:
                ret = entity_parser.data_model_to_json(data_models)
            return JSONResponse(ret, media_type="application/ld+json")
        # Default JSON
        return data_models

    def _set_route_post_predict(self, app: FastAPI,
                                description: str = "Predict an entity") -> FastAPI:
        """Set the post-predict route.

        Args:
            app (FastAPI)
            description (str): Route description.
                Defaults to "Predict an entity".

        Raises:
            HTTPException

        Returns:
            FastAPI
        """
        @app.post(
            "/predict",
            description=description,
            responses={
                200: self._get_default_ok_response()
            }
        )
        def predict(
            request: Request,
            entity_id: str = Body(description="Id of an entity"),
            post_to_broker: bool = Body(True, description="Post the predicted "
                                        "entity to the context broker"),
        ) -> Union[List[self.base_dm], Any]:
            accept = request.headers.get("accept", "application/json")
            try:
                data_model = self.context_cli.get_entity(entity_id)
                if data_model is None:
                    logger.error(f"Entity not found: {entity_id}")
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        f"Entity not found: {entity_id}"
                    )
            except KeyError as e:
                logger.error(e, exc_info=True)
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    f"Unprocessable entity type: {entity_id}"
                )
            dms = self._predict_entity(
                data_model=data_model,
                post_to_broker=post_to_broker
            )
            return self._return_data_model_for_accept(dms, accept)
        return app

    def _set_routes(self, app: FastAPI) -> FastAPI:
        """Create the API routes.

        Args:
            app (FastAPI).

        Returns:
            FastAPI.
        """
        app = self._set_route_get_root(app)
        app = self._set_route_post_notification(app)
        app = self._set_route_post_predict(app)
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
        if self.allowed_origins:
            app.add_middleware(
                Middleware(CORSMiddleware, allow_origins=self.allowed_origins)
            )
        app = self._set_routes(app)
        return app

    def run(self):
        """Parse the command-line arguments and run the API server.
        """
        args = self._parse_args()
        self._initialize(args)
        self.api = self._server()
        uvicorn.run(self.api, host=self.host, port=self.port)
        self._end()
