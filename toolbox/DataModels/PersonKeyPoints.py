from typing import List, Optional

from pydantic import Field

from toolbox.Structures import BoundingBox, Keypoints

from .BaseModel import BaseModel
from .DataModelsCatalog import register_data_model


@register_data_model
class PersonKeyPoints(BaseModel):
    """A data model for person-keypoints predictions.

    Attributes:
        id (str): Unique identifier of the entity.
        dateObserved (datetime): Entity creation time.
        image (str): Optional source image.
        bounding_box (BoundingBox): Bounding box of the detected person.
        confidence (float): Confidence of the detection.
        keypoints: (Keypoints.COCOKeypoints): Keypoints of the
            detected person.

    Methods:
        get_context() -> List[str]
        pretty()

    Properties (read-only):    
        entity_type (str): Name of the entity type.
    """
    __entity_type__ = "PersonKeyPoints"

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

    __rel_attrs__ = {"image"}

    def get_context(self) -> List[str]:
        return []

    class Config:
        schema_extra = {
            "description": """Data model intended to store information about
                the predicted keypoints of a person."""
        }
