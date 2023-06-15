from typing import Optional

from pydantic import Field

from toolbox.Structures import BoundingBox, SegmentationMask

from .BaseModel import BaseModel
from .DataModelsCatalog import register_data_model


@register_data_model
class InstanceSegmentation(BaseModel):
    """This data model stores information about segmented objects on an image.
    It is intended to be used with instance segmentation algorithms to detect
    objects and infer a segmentation mask.
    """

    __rel_attrs__ = {"image"}
    __context__ = set()

    #: The data model type ("InstanceSegmentation"). Should not be changed.
    type: str = Field("InstanceSegmentation")

    #: Id of the source image
    image: Optional[str] = Field(
        None,
        description="Id of the source image"
    )

    #: Segmentation mask of the detected instance
    mask: Optional[SegmentationMask] = Field(
        None,
        description="Segmentation mask of the detected instance",
    )

    #: Bounding box of the detected instance
    bounding_box: Optional[BoundingBox] = Field(
        None,
        description="Bounding box of the detected instance",
        alias="boundingBox"
    )

    #: Name of the predicted class
    label: Optional[str] = Field(
        None,
        description="Name of the predicted class"
    )

    #: Id of the label
    label_id: Optional[int] = Field(
        None,
        description="Id of the label",
        alias="labelId"
    )

    #: Confidence of the detection
    confidence: Optional[float] = Field(
        None,
        description="Confidence of the detection",
    )

    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "description": "This entity stores information about segmented "
            "objects on an image. It is intended to be used with instance "
            "segmentation algorithms to detect objects and infer a "
            "segmentation mask"
        }
