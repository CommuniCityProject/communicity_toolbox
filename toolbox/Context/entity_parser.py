import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Type, Union

import numpy as np
from ngsildclient import Entity
from ngsildclient.utils.uuid import uuidshortener

from toolbox.DataModels import BaseModel
from toolbox.DataModels.DataModelsCatalog import data_models_catalog
from toolbox.Structures import BoundingBox, Image, Keypoints, SegmentationMask


def create_random_id(
    entity_type: str = "",
    prefix: str = "urn:ngsi-ld:",
    uuid4: bool = False,
    shortener: bool = True
) -> str:
    """Create a random URN ID with the entity type and a UUID.

    Args:
        entity_type (str, optional): The type of the entity. Defaults to "".
        prefix (str, optional): Optional prefix to include at the start of the
            id. Defaults to "urn:ngsi-ld".
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


def data_model_to_json(data_model: Type[BaseModel]) -> dict:
    """Parse a toolbox data model to an NGSI-LD entity JSON.
    If the data model id is None, a new one will be set.

    Args:
        data_model (Type[BaseModel]): The toolbox data model object to parse.

    Returns:
        dict: The parsed data model as a NGSI-LD entity JSON.
    """
    if not data_model.id:
        data_model.id = create_random_id(entity_type=data_model.type)
    entity = Entity(data_model.type, data_model.id)

    # Set the context
    entity.ctx += data_model.context
    # Set dateCreated attribute
    entity.tprop("dateCreated", datetime.now())
    # Set dateModified attribute
    entity.tprop("dateModified", datetime.now())
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
    return json.loads(entity.to_json())


def get_entity_field(field: any, field_type: any) -> any:
    """Convert a field from an entity to its data type.

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
        if field_type.__origin__ is Union:
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


def parse_entity(entity: dict, data_model_type: Type[BaseModel]
                 ) -> Type[BaseModel]:
    """Parse an NGSI-LD JSON entity and convert it to a toolbox data model.

    Args:
        entity (dict): The entity dictionary to be parsed.
        data_model_type (Type[BaseModel]): The data model class to which
            convert the entity. One from :mod:`toolbox.DataModels`.

    Raises:
        TypeError: If the entity type does not match the data model type.
        ValueError: If the entity does not have a field that is required by
            the data model.

    Returns:
        Type[BaseModel]: The parsed entity.
    """
    params = {}
    for name, field in data_model_type.__fields__.items():
        if name == "id":
            params["id"] = entity["id"]
        elif name == "type":
            if entity["type"] != data_model_type.get_type():
                raise TypeError(f"Entity type {entity['type']} does not "
                                f"match with data model type {data_model_type}"
                                f" ({data_model_type.get_type()})")
        elif field.alias in entity:
            if "value" in entity[field.alias]:
                k = "value"
            elif "@value" in entity[field.alias]:
                k = "@value"
            elif "object" in entity[field.alias]:
                k = "object"
            else:
                raise ValueError(
                    f"Can not parse field {field.alias} "
                    f"({entity[field.alias]}) from {entity} to "
                    f"{data_model_type} type)")
            params[field.alias] = get_entity_field(
                entity[field.alias][k], field.type_
            )
        else:
            params[field.alias] = None
    return data_model_type(**params)


def json_to_data_model(entity: dict) -> Type[BaseModel]:
    """Parse an entity from a dict to a toolbox data model object.

    Args:
        entity (dict): A ngsi-ld entity as a dict.

    Raises:
        KeyError: If the entity type is not recognized.

    Returns:
        Type[BaseModel]: A data model object.
    """
    entity_type = entity["type"]
    if entity_type not in data_models_catalog:
        raise KeyError(f"Entity type {entity_type} not registered" +
                       f" in data models catalog {data_models_catalog}")
    data_model_cls = data_models_catalog[entity_type]
    return parse_entity(entity, data_model_cls)
