from typing import List, Type

from toolbox import DataModels
from toolbox.Projects.AgeGender import AgeGender
from toolbox.utils.DemoBase import DemoBase
from toolbox.Structures import Image



class Demo(DemoBase):

    def __init__(self):
        super().__init__()
    
    def _load_model(self, config: dict, task: str):
        if task != "visualize":
            self.model = AgeGender(config)

    def _process_image(self, image: Image) -> List[DataModels.Face]:
        data_models = self.model.predict(image)
        return data_models
    
    def _consume_data_model(self, data_model: Type[DataModels.BaseModel]
        ) -> List[DataModels.Face]:
        if isinstance(data_model, DataModels.Face):
            assert data_model.image, data_model.image
            img_dm = self.context_cli.get_entity(data_model.image)
            image = Image(img_dm.url)
            new_dm = self.model.update_face(image, data_model)
            return [new_dm]
        elif isinstance(data_model, DataModels.Image):
            image = Image(data_model.url, id=data_model.id)
            return self.model.predict(image)
        else:
            raise ValueError(f"Can not process entity type {type(data_model)}")


def main():
    demo = Demo()
    demo.run()

if __name__ == "__main__":
    main()
