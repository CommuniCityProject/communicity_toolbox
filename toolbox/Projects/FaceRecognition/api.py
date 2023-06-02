from typing import List, Any, Union
import argparse

from fastapi import FastAPI, Body, HTTPException, status, Request

from toolbox import DataModels
from toolbox.Projects.FaceRecognition import FaceRecognition
from toolbox.utils.ApiBase import ApiBase
from toolbox.utils.utils import get_logger

logger = get_logger("FaceRecognitionApi")



class FaceRecognitionApi(ApiBase):
    
    TITLE = "Face Recognition API"

    def __init__(self):
        super().__init__(DataModels.Face)

    def _initialize(self, args: argparse.Namespace):
        """Initialize the model.
        """
        super()._initialize(args)
        self._do_extraction = self.config["api"]["do_feature_extraction"]
        self._do_recognition = self.config["api"]["do_feature_recognition"]
        self._update_entity = self.config["api"]["update_entity"]
        self._post_new_entity = self.config["api"]["post_new_entity"]
        self._model = FaceRecognition(
            self.config,
            do_extraction=self._do_extraction,
            do_recognition=self._do_recognition
        )

    def _predict_entity(self,
        data_model: Union[DataModels.Image, DataModels.Face],
        post_to_broker: bool) -> List[DataModels.Face]:
        """Predict a data model.

        Args:
            data_model (Union[DataModels.Image, DataModels.Face]): A Face
                or an Image data model.
            post_to_broker (bool): Post the predicted data models to the
                context broker.

        Raises:
            HTTPException: If the data model is not a Face or an Image.

        Returns:
            List[DataModels.Face]: The predicted Face data models.
        """
        if isinstance(data_model, DataModels.Image):
            image = self._get_image_from_dm(data_model)
            dms = self._model.predict(image)
            for dm in dms:
                self._model.recognize(dm)
                if post_to_broker:
                    self.context_cli.post_data_model(dm)
            return dms
        elif isinstance(data_model, DataModels.Face):
            if data_model.recognized:
                return [data_model]
            image = self._get_image_by_id(data_model.image)
            dm = self._model.update_face(image, data_model)
            self._model.recognize(dm)
            if post_to_broker:
                if self._post_new_entity:
                    dm.id = None
                    self.context_cli.post_data_model(dm)
                else:
                    self.context_cli.update_data_model(dm)
            return [dm]
        else:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Unprocessable entity type: {type(data_model)}"
            )
        
    def _extract_entity(self,
        data_model: Union[DataModels.Image, DataModels.Face],
        post_to_broker: bool) -> List[DataModels.Face]:
        """Extract features from a data model.

        Args:
            data_model (Union[DataModels.Image, DataModels.Face]): A Face
                or an Image data model.
            post_to_broker (bool): Post the predicted data models to the
                context broker.

        Raises:
            HTTPException: If the data model is not a Face or an Image.

        Returns:
            List[DataModels.Face]: The predicted Face data models.
        """
        if isinstance(data_model, DataModels.Image):
            image = self._get_image_from_dm(data_model)
            dms = self._model.predict(image)
            if post_to_broker:
                [self.context_cli.post_data_model(dm) for dm in dms]
            return dms
        elif isinstance(data_model, DataModels.Face):
            if data_model.features is not None:
                return [data_model]
            image = self._get_image_by_id(data_model.image)
            dm = self._model.update_face(image, data_model)
            if post_to_broker:
                if self._post_new_entity:
                    dm.id = None
                    self.context_cli.post_data_model(dm)
                else:
                    self.context_cli.update_data_model(dm)
            return [dm]
        else:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Unprocessable entity type: {type(data_model)}"
            )

    def _set_route_post_extract(self, app: FastAPI) -> FastAPI:
        """Set the post-extract-features route.

        Args:
            app (FastAPI)

        Raises:
            HTTPException

        Returns:
            FastAPI
        """
        @app.post(
            "/extract",
            responses={
                404: {"description": "Entity not found"},
                200: self._get_default_ok_response()
            }
        )
        def extract(
            request: Request,
            entity_id: str = Body(description="Id of an entity"),
            post_to_broker: bool = Body(True, description="""Post the
                predicted entity to the context broker"""),
        ) -> Union[List[self.base_dm], Any]:
            """Extract the features of a Face or an Image entity.
            """
            accept = request.headers.get("accept", "application/json")
            try:
                data_model = self.context_cli.get_entity(entity_id)
                if data_model is None:
                    logger.error(f"Entity not found: {entity_id}")
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        "Entity not found"
                    )
            except KeyError as e:
                logger.error(e, exc_info=True)
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    f"Unprocessable entity type: {entity_id}"
                )
            dms = self._extract_entity(
                data_model=data_model,
                post_to_broker=post_to_broker
            )
            return self._return_data_model_for_accept(dms, accept)
        return app
    
    def _recognize_entity(self,
        data_model: DataModels.Face, post_to_broker: bool) -> DataModels.Face:
        """Recognize the face features of a Face data model.

        Args:
            data_model (DataModels): A Face data model.
            post_to_broker (bool): Post the predicted data model to the
                context broker.

        Raises:
            HTTPException: If the data model is not a Face.

        Returns:
            List[DataModels.Face]: The predicted Face data model.
        """
        if isinstance(data_model, DataModels.Face):
            if data_model.recognized:
                return [data_model]
            if not isinstance(data_model.features, list):
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    f"The given entity has no features to recognize"
                )
            rec_dm = self._model.recognize(data_model)
            if post_to_broker:
                if self._update_entity:
                    self.context_cli.update_data_model(rec_dm)
                if self._post_new_entity:
                    rec_dm.id = None
                    self.context_cli.post_data_model(rec_dm)
            return rec_dm
        else:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Unprocessable entity type: {type(data_model)}"
            )

    def _set_route_post_recognize(self, app: FastAPI) -> FastAPI:
        """Set the post-recognize-features route.

        Args:
            app (FastAPI)

        Raises:
            HTTPException

        Returns:
            FastAPI
        """
        @app.post(
            "/recognize",
            responses={
                404: {"description": "Entity not found"},
                200: self._get_default_ok_response()
            }
        )
        def recognize(
            request: Request,
            entity_id: str = Body(
                description="Id of a Face entity"),
            post_to_broker: bool = Body(True,
                description="Post the predicted entity to the context broker")
        ) -> Union[self.base_dm, Any]:
            """Recognize the features of a Face entity.
            """
            accept = request.headers.get("accept", "application/json")
            try:
                data_model = self.context_cli.get_entity(entity_id)
                if data_model is None:
                    logger.error(f"Entity not found: {entity_id}")
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        "Entity not found"
                    )
            except KeyError as e:
                logger.error(e, exc_info=True)
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    f"Unprocessable entity type: {entity_id}"
                )
            rec_dm = self._recognize_entity(
                data_model=data_model,
                post_to_broker=post_to_broker
            )
            return self._return_data_model_for_accept(rec_dm, accept)
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
        if self._do_extraction and self._do_recognition:
            app = self._set_route_post_predict(
                app,
                description="Extract features and recognize faces on an "\
                    "Image or a Face entity"
            )
        if self._do_recognition:
            app = self._set_route_post_recognize(app)
        if self._do_extraction:
            app = self._set_route_post_extract(app)
        return app
    
def main():
    api = FaceRecognitionApi()
    api.run()


if __name__ == "__main__":
    main()
