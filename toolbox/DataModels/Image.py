from pydantic import Field

from .BaseModel import BaseModel
from .DataModelsCatalog import register_data_model


@register_data_model
class Image(BaseModel):
    """This data model stores information about an image file that is uploaded
    to a server from a camera or any other source, and that is available to
    other services.
    """

    __rel_attrs__ = set()
    __context__ = set()

    #: The data model type ("Image"). Should not be changed.
    type: str = Field("Image")

    #: Width of the image in pixels
    width: int = Field(
        description="Width of the image in pixels",
    )

    #: Height of the image in pixels
    height: int = Field(
        description="Height of the image in pixels",
    )

    #: Local file path to the image within the storage host
    path: str = Field(
        "",
        description="Local file path to the image within the storage host"
    )

    #: URL to the image
    url: str = Field(
        "",
        description="URL to the image"
    )

    #: The ID of the entity that created the image or a text
    #: describing the source of the image
    source: str = Field(
        "",
        description="The ID of the entity that created the image or a text "
        "describing the source of the image."
    )

    #: The purpose of the image, if any
    purpose: str = Field(
        "",
        description="The purpose of the image, if any"
    )

    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "description": "This entity stores information about an image "
            "file that is uploaded to a server from a camera or any other "
            "source, and that is available to other services"
        }
