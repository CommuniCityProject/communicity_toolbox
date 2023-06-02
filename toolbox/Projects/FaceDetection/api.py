from typing import List, Union
import argparse

from fastapi import status, HTTPException

from toolbox import DataModels
from toolbox.Projects.FaceDetection import FaceDetection
from toolbox.utils.ApiBase import ApiBase
from toolbox.utils.utils import get_logger

logger = get_logger("toolbox.FaceDetectionApi")



class FaceDetectionApi(ApiBase):
    
    TITLE = "Face Detection API"

    def __init__(self):
        super().__init__(DataModels.Face)

    def _initialize(self, args: argparse.Namespace):
        """Initialize the model.
        """
        super()._initialize(args)
        self._model = FaceDetection(self.config)
    
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
            if post_to_broker:
                [self.context_cli.post_data_model(dm) for dm in dms]
            return dms
        else:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Unprocessable entity type: {type(data_model)}"
            )
        
        
def main():
    api = FaceDetectionApi()
    api.run()


if __name__ == "__main__":
    main()
