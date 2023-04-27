from typing import List

from pydantic import Field

from .BaseModel import BaseModel
from .DataModelsCatalog import register_data_model


@register_data_model
class Image(BaseModel):
    """Data model for Images.

    Attributes:
        id (str): Unique identifier of the entity.
        dateObserved (datetime): Entity creation time.
        width (int): Width of the image in pixels.
        height (int): Height of the image in pixels.
        path (str): Path to the image.
        url (str): URL to the image.
        source (str): Source of the image.
        purpose (str): The purpose of the image.

    Methods:
        get_context() -> List[str]
        pretty()

    Properties (read-only):    
        entity_type (str): Name of the entity type.
    """
    __entity_type__ = "Image"

    width: int = Field(
        description="Width of the image in pixels",
    )
    height: int = Field(
        description="Height of the image in pixels",
    )
    path: str = Field(
        "",
        description="Path to the image"
    )
    url: str = Field(
        "",
        description="URL to the image"
    )
    source: str = Field(
        "",
        description="The source of the image"
    )
    purpose: str = Field(
        "",
        description="The purpose of the image"
    )

    def get_context(self) -> List[str]:
        return []

    class Config:
        schema_extra = {
            "description": """Data model intended to store information about
                an Image."""
        }
