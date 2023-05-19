from typing import List, Type

from toolbox import DataModels
from toolbox.Projects.InstanceSegmentation import InstanceSegmentation
from toolbox.utils.DemoBase import DemoBase
from toolbox.Structures import Image



class Demo(DemoBase):

    def __init__(self):
        super().__init__()
    
    def _load_model(self, config: dict, task: str):
        if task != "visualize":
            self.model = InstanceSegmentation(config)

    def _process_image(self, image: Image
        ) -> List[DataModels.InstanceSegmentation]:
        data_models = self.model.predict(image)
        return data_models

    def _consume_data_model(self, data_model: Type[DataModels.BaseModel]
        ) -> List[DataModels.InstanceSegmentation]:
        if isinstance(data_model, DataModels.Image):
            image = Image(data_model.url, id=data_model.id)
            return self.model.predict(image)
        else:
            raise ValueError(f"Can not process entity type {type(data_model)}")

def main():
    demo = Demo()
    demo.run()

if __name__ == "__main__":
    main()
