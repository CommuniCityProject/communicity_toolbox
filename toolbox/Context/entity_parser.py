import typing
import uuid
from datetime import datetime
from enum import Enum

import numpy as np
from ngsildclient import Entity
from ngsildclient.utils.uuid import uuidshortener

from toolbox.DataModels import BaseModel
from toolbox.Structures import BoundingBox, Image, Keypoints, SegmentationMask


def create_random_id(entity_type: str = "", prefix: str = "urn:ngsi-ld:",
                     uuid4: bool = False, shortener: bool = True) -> str:
    """Create a random URN id with the entity type and a UUID.

    Args:
        entity_type (str, optional): The type of the entity. Defaults to "".
        prefix (str, optional): Optional prefix to include at the start of the
            id. Defaults to urn:ngsi-ld".
        uuid4 (bool, optional): If UUID4 should be used instead of UUID1.
            Defaults to False.
        shortener (bool, optional): Use a shorter version of the UUID. Defaults
            to True.

    Returns:
        str: A random id.
    """
    _uuid = uuid.uuid4() if uuid4 else uuid.uuid1()
    _uuid = uuidshortener(_uuid) if shortener else str(_uuid)
    return (
        prefix +
        (f"{entity_type}:" if entity_type else "") +
        _uuid
    )


def set_entity_field(entity: Entity, field: any, name: str):
    """Parse and add a new field to an NGSI-LD entity.

    Args:
        entity (Entity): The Entity object to add a field.
        field (any): The value to be added.
        name (str): The field name.
    """
    t = type(field)
    if t in (BoundingBox, SegmentationMask, Image) or \
            isinstance(field, Keypoints.BaseKeypoints):
        entity.prop(name, field.serialize())
    elif isinstance(t, np.ndarray):
        entity.prop(name, field.tolist())
    elif isinstance(field, Enum):
        entity.prop(name, str(field))
    else:
        entity.prop(name, field)


def create_entity(data_model: typing.Type[BaseModel]) -> Entity:
    """Create an NGSI-LD Entity object from a data model.
    If the data model id is None, a new id will be created and set.

    Args:
        data_model (Type[BaseModel]): The model from which build the entity.

    Returns:
        Entity: The created NGSI-LD entity object.
    """
    if not data_model.id:
        data_model.id = create_random_id(
            entity_type=data_model.entity_type
        )
    entity = Entity(data_model.entity_type, data_model.id)
    
    # Set the context
    entity.ctx += data_model.get_context()
    # Set dateObserved attribute
    entity.tprop("dateObserved", data_model.dateObserved)
    # Set relationship attributes
    rel_attrs = data_model.rel_attrs
    for rel in rel_attrs:
        value = getattr(data_model, rel)
        if value is not None:
            entity.rel(rel, value)

    # Set the rest of attributes
    data_model_dict = data_model.dict(
        exclude={"id", "dateObserved", "type"}.union(rel_attrs),
        by_alias=True
    )
    for name, value in data_model_dict.items():
        if value is not None:
            set_entity_field(entity, value, name)
    return entity


def get_entity_field(field: any, field_type: any) -> any:
    """Cast a field from an entity to its data type.

    Args:
        field (any): The field value.
        field_type (any): The data type to which cast the field.

    Returns:
        any: The field converted to the data type.
    """
    # Toolbox structures
    if field_type in (BoundingBox, Image, SegmentationMask):
        return field_type.deserialize(field)
    # datetime
    elif field_type is datetime:
        return datetime.fromisoformat(field["@value"][:-1])
    # numpy array
    elif field_type is np.ndarray:
        return np.array(field)
    # keypoints
    elif issubclass(field_type, Keypoints.BaseKeypoints):
        return field_type.deserialize(field)
    # Typing
    elif hasattr(field_type, "__origin__"):
        if field_type.__origin__ is typing.Union:
            return get_entity_field(field, field_type.__args__[0])
    # Enums
    elif hasattr(field_type, "__base__") and field_type.__base__ is Enum:
        return field_type[field]
    try:
        return field_type(field)
    except Exception as e:
        raise ValueError(
            f"Can not parse value {field} to {field_type}. " + str(e)
        )


def parse_entity(entity: typing.Union[Entity, dict],
                 data_model_type: typing.Type[BaseModel]
                 ) -> typing.Type[BaseModel]:
    """Parses a NGSI-LD entity and convert it to a toolbox data model.

    Args:
        entity (Entity): The entity to be parsed.
        data_model_type (Type[BaseModel]): The data model class to which
            convert the entity. One from toolbox.DataModels.

    Returns:
        Type[BaseModel]: The parsed entity.
    """
    params = {}
    for name, field in data_model_type.__fields__.items():
        if name == "id":
            params["id"] = entity["id"]
        elif field.alias in entity:
            if "value" in entity[field.alias]:
                k = "value"
            elif "@value" in entity[field.alias]:
                k = "@value"
            elif "object" in entity[field.alias]:
                k = "object"
            else:
                raise ValueError(f"Can not parse field {entity[field.alias]}")
            params[field.alias] = get_entity_field(
                entity[field.alias][k], field.type_
            )
        else:
            params[field.alias] = None
    return data_model_type(**params)
