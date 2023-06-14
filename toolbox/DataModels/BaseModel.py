from __future__ import annotations

import math
from datetime import datetime
from typing import Optional, Set

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from toolbox.utils.utils import str_separator


class BaseModel(PydanticBaseModel):
    """Base class for the toolbox data models.

    Attributes to override:
        __rel_attrs__ (set): Set of attributes names that are relationships.
        __context__ (set): Set of context URIs.
        type (Field): Data model type name.
    """

    __rel_attrs__ = set()
    __context__ = set()

    id: Optional[str] = Field(
        None,
        description="Unique identifier of the entity"
    )

    dateObserved: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="Entity creation time"
    )

    type: str = Field(
        "BaseModel",
        const=True,
        description="Name of the entity type"
    )

    class Config:
        # Pydantic configuration
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

    @property
    def rel_attrs(self) -> Set[str]:
        """Return a set with the names of the attributes that are relationships.
        """
        return self.__rel_attrs__

    @property
    def context(self) -> Set[str]:
        """Return a set with the context URLs of the entity.
        """
        return self.__context__

    def pretty(self) -> str:
        """Return a pretty description of the object. 
        """
        names = list(self.__fields__.keys())
        max_n = max([len(n) for n in names]) - 1
        tab_size = 8
        extra_tab = 1
        length = math.ceil((max_n + (tab_size*extra_tab)) / 8) * tab_size

        r = str_separator(title=self.type)
        for name in names:
            r += name
            r += "\t" * math.ceil((length - len(name))/tab_size)
            r += str(getattr(self, name))
            r += "\n"
        r += str_separator()
        return r

    @classmethod
    def get_type(cls) -> str:
        """Static methods to get the data model type name.
        """
        return cls.__fields__["type"].default
