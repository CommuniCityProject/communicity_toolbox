from typing import List, Optional

from pydantic import Field

from toolbox.Structures import BoundingBox, SegmentationMask

from .BaseModel import BaseModel
from .DataModelsCatalog import register_data_model


@register_data_model
class InstanceSegmentation(BaseModel):
    """A data model for instance segmentation tasks.

    Attributes:
        id (str): Unique identifier of the entity.
        dateObserved (datetime): Entity creation time.
        image (str): Optional source image.
        mask (SegmentationMask): Segmentation mask of the detected instance.
        bounding_box (BoundingBox): Bounding box of the detected instance.
        label (str): Name of the predicted class.
        label_id (int): Id of the label.
        confidence (float): Confidence of the detection.

    Methods:
        get_context() -> List[str]
        pretty()

    Properties (read-only):    
        entity_type (str): Name of the entity type.
    """
    __entity_type__ = "InstanceSegmentation"

    image: Optional[str] = Field(
        None,
        description="Id of the source image"
    )
    mask: Optional[SegmentationMask] = Field(
        None,
        description="Segmentation mask of the detected instance",
    )
    bounding_box: Optional[BoundingBox] = Field(
        None,
        description="Bounding box of the detected instance",
        alias="boundingBox"
    )
    label: Optional[str] = Field(
        None,
        description="Name of the predicted class"
    )
    label_id: Optional[int] = Field(
        None,
        description="Id of the label",
        alias="labelId"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence of the detection",
    )

    __rel_attrs__ = {"image"}

    def get_context(self) -> List[str]:
        return []

    class Config:
        schema_extra = {
            "description": """Data model intended to store information about
                an instance segmentation."""
        }
