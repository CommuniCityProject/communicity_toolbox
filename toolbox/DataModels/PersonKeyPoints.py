from typing import Optional

from pydantic import Field

from toolbox.Structures import BoundingBox, Keypoints

from .BaseModel import BaseModel
from .DataModelsCatalog import register_data_model


@register_data_model
class PersonKeyPoints(BaseModel):
    """This data model stores information about a set of body-keypoints of an
    image of a person. It is intended to be used with computer vision algorithms
    to infer the position of different parts of the body from an image.
    """

    __rel_attrs__ = {"image"}
    __context__ = set()

    type: str = Field("PersonKeyPoints")

    image: Optional[str] = Field(
        None,
        description="Id of the source image"
    )
    bounding_box: Optional[BoundingBox] = Field(
        description="Bounding box of the detected person",
        alias="boundingBox"
    )
    confidence: Optional[float] = Field(
        description="Confidence of the detection",
    )
    keypoints: Optional[Keypoints.COCOKeypoints] = Field(
        description="Keypoints of the detected person"
    )

    class Config:
        schema_extra = {
            "description": "This entity stores information about a set of "
            "body-keypoints of an image of a person. It is intended to be "
            "used with computer vision algorithms to infer the position of "
            "different parts of the body from an image"
        }
