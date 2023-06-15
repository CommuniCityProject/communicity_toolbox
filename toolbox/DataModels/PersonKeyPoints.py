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

    #: The data model type ("PersonKeyPoints"). Should not be changed.
    type: str = Field("PersonKeyPoints")

    #: Id of the source image
    image: Optional[str] = Field(
        None,
        description="Id of the source image"
    )

    #: Bounding box of the detected person
    bounding_box: Optional[BoundingBox] = Field(
        description="Bounding box of the detected person",
        alias="boundingBox"
    )

    #: Confidence of the detection
    confidence: Optional[float] = Field(
        description="Confidence of the detection",
    )

    #: Keypoints of the detected person
    keypoints: Optional[Keypoints.COCOKeypoints] = Field(
        description="Keypoints of the detected person"
    )

    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "description": "This entity stores information about a set of "
            "body-keypoints of an image of a person. It is intended to be "
            "used with computer vision algorithms to infer the position of "
            "different parts of the body from an image"
        }
