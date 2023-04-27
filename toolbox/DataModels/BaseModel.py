from __future__ import annotations

import math
from datetime import datetime
from typing import List, Optional, Set

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from toolbox.utils.utils import str_separator


class BaseModel(PydanticBaseModel):
    """Base class for the toolbox data models.

    Methods to be implemented:
        get_context() -> List[str]

    Attributes to override:
        __entity_type__

    Raises:
        NotImplementedError

    Attributes:
        id (str)
        dateObserved (datetime)

    Methods:
        pretty()

    Properties (read-only):
        entity_type (str): Name of the entity type.
    """
    __entity_type__ = "BaseModel"
    __rel_attrs__ = set()

    id: Optional[str] = Field(
        None,
        description="Unique identifier of the entity"
    )

    dateObserved: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="Entity creation time"
    )

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

    @classmethod
    @property
    def entity_type(cls) -> str:
        return cls.__entity_type__

    @property
    def rel_attrs(self) -> Set[str]:
        return self.__rel_attrs__

    def get_context(self) -> List[str]:
        """Return a list with the context of the entities.

        Raises:
            NotImplementedError: To be implemented.

        Returns:
            List[str]: A list of URIs.
        """
        raise NotImplementedError

    def pretty(self) -> str:
        """Return a pretty description of the object. 
        """
        names = list(self.__fields__.keys())
        max_n = max([len(n) for n in names]) - 1
        tab_size = 8
        extra_tab = 1
        length = math.ceil((max_n + (tab_size*extra_tab)) / 8) * tab_size

        r = str_separator(title=self.entity_type)
        for name in names:
            r += name
            r += "\t" * math.ceil((length - len(name))/tab_size)
            r += str(getattr(self, name))
            r += "\n"
        r += str_separator()
        return r
