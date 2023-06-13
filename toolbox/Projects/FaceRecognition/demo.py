from typing import List

from toolbox import DataModels
from toolbox.Projects.FaceRecognition import FaceRecognition
from toolbox.Structures import Image
from toolbox.utils.DemoBase import DemoBase


class Demo(DemoBase):

    def __init__(self):
        super().__init__()

    def _load_model(self, config: dict, task: str):
        if task != "visualize":
            self.model = FaceRecognition(
                config,
                do_extraction=config["api"]["do_feature_extraction"],
                do_recognition=config["api"]["do_feature_recognition"]
            )

    def _process_image(self, image: Image) -> List[DataModels.Face]:
        data_models = self.model.predict(image)
        if self.model.do_recognition:
            [self.model.recognize(dm) for dm in data_models]
        return data_models

    def _consume_data_model(self, data_model: DataModels.Face
                            ) -> List[DataModels.Face]:
        if isinstance(data_model, DataModels.Face):
            # Extract
            if not isinstance(data_model.features, list):
                if not self.model.do_extraction:
                    raise ValueError(
                        "Can not process Face entity without features"
                    )
                img_dm = self.context_cli.get_entity(data_model.image)
                image = Image(img_dm.url)
                data_model = self.model.update_face(image, data_model)
            # Recognize
            if self.model.do_extraction:
                data_model = self.model.recognize(data_model)
            return [data_model]
        elif isinstance(data_model, DataModels.Image):
            image = Image(data_model.url, id=data_model.id)
            faces = self.model.predict(image)
            if self.model.do_extraction:
                faces = [self.model.recognize(face) for face in faces]
            return faces
        else:
            raise ValueError(f"Can not process entity type {type(data_model)}")


def main():
    demo = Demo()
    demo.run()


if __name__ == "__main__":
    main()
