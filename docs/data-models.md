# Toolbox Data Models

The publication and consumption of NGSI entities is done following the data models defined in the Toolbox. To facilitate the management of this data, a set of Python classes is provided as well.

The developed data models are listed here:

| Name | Description | Specification | Python class |
|------|-------------|---------------|--------------|
| Face | Store information about some inferred attributes about a Face | [schema.json](./DataModels/Face/schema.json) | [Face.py](../toolbox/DataModels/Face.py)
| InstanceSegmentation | Store information about a segmented object in an image | [schema.json](./DataModels/InstanceSegmentation/schema.json) | [InstanceSegmentation.py](../toolbox/DataModels/InstanceSegmentation.py)
| PersonKeyPoints | Store the position of different body parts within an image | [schema.json](./DataModels/PersonKeyPoints/schema.json) | [PersonKeyPoints.py](../toolbox/DataModels/PersonKeyPoints.py)
| Image | Stores information about an uploaded image | [schema.json](./DataModels/Image/schema.json) | [Image.py](../toolbox/DataModels/Image.py)