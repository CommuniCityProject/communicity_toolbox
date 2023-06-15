# Toolbox Data Models

The publication and consumption of NGSI entities are done following the data models defined in the Toolbox. Their specifications can be found [here](https://github.com/CommuniCityProject/communicity_toolbox/tree/master/docs/DataModels). To facilitate the management of this data, a set of Python classes is provided as well.

The developed data models are listed here:

| Name | Description | Specification | Python class |
|------|-------------|---------------|--------------|
| Face | Store information about some inferred attributes about a Face | [schema.json](./DataModels/Face/schema.json) | [Face.py](https://communicity-docs.readthedocs.io/en/latest/docs/toolbox/DataModels.html#module-DataModels.Face)
| InstanceSegmentation | Store information about a segmented object in an image | [schema.json](./DataModels/InstanceSegmentation/schema.json) | [InstanceSegmentation.py](https://communicity-docs.readthedocs.io/en/latest/docs/toolbox/DataModels.html#module-DataModels.InstanceSegmentation)
| PersonKeyPoints | Store the position of different body parts within an image | [schema.json](./DataModels/PersonKeyPoints/schema.json) | [PersonKeyPoints.py](https://communicity-docs.readthedocs.io/en/latest/docs/toolbox/DataModels.html#module-DataModels.PersonKeyPoints)
| Image | Stores information about an uploaded image | [schema.json](./DataModels/Image/schema.json) | [Image.py](https://communicity-docs.readthedocs.io/en/latest/docs/toolbox/DataModels.html#module-DataModels.Image)