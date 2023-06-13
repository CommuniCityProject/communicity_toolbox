import argparse
from typing import List

from fastapi import HTTPException, status

from toolbox import DataModels
from toolbox.Projects.InstanceSegmentation import InstanceSegmentation
from toolbox.utils.ApiBase import ApiBase
from toolbox.utils.utils import get_logger

logger = get_logger("toolbox.InstanceSegmentationApi")


class InstanceSegmentationApi(ApiBase):

    TITLE = "Instance Segmentation API"

    def __init__(self):
        super().__init__(DataModels.InstanceSegmentation)

    def _initialize(self, args: argparse.Namespace):
        """Initialize the model.
        """
        super()._initialize(args)
        self._model = InstanceSegmentation(self.config)

    def _predict_entity(self,
                        data_model: DataModels.Image,
                        post_to_broker: bool) -> List[DataModels.Face]:
        """Predict a data model.

        Args:
            data_model (DataModels.Image): An Image data model.
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
    api = InstanceSegmentationApi()
    api.run()


if __name__ == "__main__":
    main()
