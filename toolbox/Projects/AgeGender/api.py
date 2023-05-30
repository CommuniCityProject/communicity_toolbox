import argparse
from typing import List, Union

from fastapi import HTTPException, status

from toolbox import DataModels
from toolbox.Projects.AgeGender import AgeGender
from toolbox.utils.ApiBase import ApiBase
from toolbox.utils.utils import get_logger

logger = get_logger("toolbox.AgeGenderApi")


class AgeGenderApi(ApiBase):

    TITLE = "Age Gender API"

    def __init__(self):
        super().__init__(DataModels.Face)

    def _initialize(self, args: argparse.Namespace):
        super()._initialize(args)
        self._post_new_entity = self.config["api"]["post_new_entity"]
        self._update_entity = self.config["api"]["update_entity"]
        self._model = AgeGender(self.config)

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
        elif isinstance(data_model, DataModels.Face):
            # Ignore already predicted entities.
            if data_model.age is not None or data_model.gender is not None \
                    or data_model.gender_confidence is not None:
                return [data_model]
            # Predict the image
            image = self._get_image_by_id(data_model.image)
            dm = self._model.update_face(image, data_model)
            if post_to_broker:
                if self._post_new_entity:
                    dm.id = None
                    self.context_cli.post_data_model(dm)
                if self._update_entity:
                    self.context_cli.update_data_model(dm)
            return [dm]
        else:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Unprocessable entity type: {type(data_model)}"
            )


def main():
    api = AgeGenderApi()
    api.run()


if __name__ == "__main__":
    main()
