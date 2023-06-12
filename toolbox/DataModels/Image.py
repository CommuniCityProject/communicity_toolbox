from pydantic import Field

from .BaseModel import BaseModel
from .DataModelsCatalog import register_data_model


@register_data_model
class Image(BaseModel):
    """This entity stores information about an image file that is uploaded to
        a server from a camera or any other source, and that is available to
        other services.

    Attributes:
        id (str)
        dateObserved (datetime)
        type (str)
        width (int)
        height (int)
        path (str)
        url (str)
        source (str)
        purpose (str)
    """
    
    __rel_attrs__ = set()
    __context__ = set()

    type: str = Field("Image")

    width: int = Field(
        description="Width of the image in pixels",
    )
    height: int = Field(
        description="Height of the image in pixels",
    )
    path: str = Field(
        "",
        description="Local file path to the image within the storage host"
    )
    url: str = Field(
        "",
        description="URL to the image"
    )
    source: str = Field(
        "",
        description="The ID of the entity that created the image or a text "
        "describing the source of the image."
    )
    purpose: str = Field(
        "",
        description="The purpose of the image, if any"
    )

    class Config:
        schema_extra = {
            "description": "This entity stores information about an image "
            "file that is uploaded to a server from a camera or any other "
            "source, and that is available to other services"
        }
