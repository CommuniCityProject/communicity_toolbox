from typing import Optional

from pydantic import Field

from toolbox.Structures import BoundingBox, SegmentationMask

from .BaseModel import BaseModel
from .DataModelsCatalog import register_data_model


@register_data_model
class InstanceSegmentation(BaseModel):
    """This entity stores information about segmented objects on an image.
    It is intended to be used with instance segmentation algorithms to detect
    objects and infer a segmentation mask.

    Attributes:
        id (str)
        dateObserved (datetime)
        type (str)
        image (str)
        mask (SegmentationMask)
        bounding_box (BoundingBox)
        label (str)
        label_id (int)
        confidence (float)
    """
    
    __rel_attrs__ = {"image"}
    __context__ = set()

    type: str = Field("InstanceSegmentation")

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

    class Config:
        schema_extra = {
            "description": "This entity stores information about segmented "
            "objects on an image. It is intended to be used with instance "
            "segmentation algorithms to detect objects and infer a "
            "segmentation mask"
        }
