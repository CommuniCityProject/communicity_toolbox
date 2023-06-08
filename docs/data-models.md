# Toolbox Data Models

The publication and consumption of NGSI entities is done following the data models defined by the Toolbox. A set of Python classes are defined to manage the data defined in these data models.

Here are described the specifications of the data models developed.

| Name | Description | Specification | Python class |
|------|-------------|---------------|--------------|
| Face | Store information about some inferred attributes about a Face | [schema.json]((./DataModels/Face/schema.json)) | [Face.py](../toolbox/DataModels/Face.py)
| InstanceSegmentation | Store information about a segmented object from an image | [schema.json]((./DataModels/InstanceSegmentation/schema.json)) | [InstanceSegmentation.py](../toolbox/DataModels/InstanceSegmentation.py)
| PersonKeyPoints | Store the position of different body parts of a person within an image | [schema.json]((./DataModels/PersonKeyPoints/schema.json)) | [PersonKeyPoints.py](../toolbox/DataModels/PersonKeyPoints.py)
| Image | Stores the information about an uploaded image | [schema.json]((./DataModels/Image/schema.json)) | [Image.py](../toolbox/DataModels/Image.py)