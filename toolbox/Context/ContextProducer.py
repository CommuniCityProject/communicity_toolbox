import json
import logging
from datetime import datetime
from typing import Type

import requests
from ngsildclient import Client

from toolbox import DataModels
from toolbox.utils.utils import get_logger

from .entity_parser import create_entity

logger = get_logger("toolbox.ContextProducer")
logging.getLogger("ngsildclient").setLevel(logging.WARNING)


class ContextProducer:
    """Manage the production of context data on a context broker.

    Methods:
        post_entity(data_model) -> dict
        to_json(data_model) -> str
        update_entity(data_model, create) -> dict
        delete_entity(entity_id) -> bool
    """

    def __init__(self, config: dict):
        """Initialize the ContextProducer.

        Args:
            config (dict): Configuration dictionary.
        """
        self._broker_host = config["context_broker"]["host"]
        self._broker_port = config["context_broker"]["port"]
        self._broker_url = f"http://{self._broker_host}:{self._broker_port}"
        self._entities_url = f"{self._broker_url}/ngsi-ld/v1/entities"
        logger.info(f"Using context broker at {self._broker_url}")
        self._broker = Client(self._broker_host, self._broker_port)

    def post_entity(self, data_model: Type[DataModels.BaseModel]) -> dict:
        """Post an entity to the context broker. If the data model id is
        None, a new one will be assigned.

        Args:
            data_model (Type[DataModels.BaseModel]): The data model object to
                upload to the context broker.

        Returns:
            dict: The uploaded json.
        """
        logger.debug(f"Posting data model to the context broker: "
                     f"\n{data_model.pretty()}")
        entity = create_entity(data_model)
        entity.tprop("dateModified", datetime.now())
        entity.tprop("dateCreated", datetime.now())
        self._broker.create(entity)
        return json.loads(entity.to_json())

    def to_json(self, data_model: Type[DataModels.BaseModel]) -> dict:
        """Convert a data model object to a json string that can be directly
        uploaded to a context broker.

        Args:
            data_model (Type[DataModels.BaseModel]): The data model object to
                convert.

        Returns:
            dict: The parsed json.
        """
        entity = create_entity(data_model)
        entity.tprop("dateModified", datetime.now())
        entity.tprop("dateCreated", datetime.now())
        return json.loads(entity.to_json())

    def update_entity(self, data_model: Type[DataModels.BaseModel],
                      create: bool = False) -> dict:
        """Update an existing entity in the context broker.

        Args:
            data_model (Type[DataModels.BaseModel]): The data model to update.
            create (bool): If the entity should be created if it does not
                exists. Defaults to False.

        Raises:
            ValueError: If the id of the ``data_model`` is None.
            ngsildclient.api.exceptions.NgsiResourceNotFoundError: If there is
                no entity with the data model id in the context broker and 
                ``create`` is False.

        Returns:
            dict: The uploaded json.
        """
        logger.debug(f"Updating data model to the context broker: "
                     f"\n{data_model.pretty()}")
        if create:
            if data_model.id is None or not self._broker.exists(data_model.id):
                logger.debug(
                    f"Data model does not exist on the context broker")
                self.post_entity(data_model)
                return
        if data_model.id is None:
            raise ValueError("Can not update entity with None id")
        orig_entity = self._broker.get(data_model.id)
        new_entity = create_entity(data_model)
        if "dateCreated" in orig_entity.to_dict():
            created = orig_entity["dateCreated"]["value"]["@value"]
            new_entity.tprop("dateCreated", created)
        new_entity.tprop("dateModified", datetime.now())
        self._broker.update(new_entity)
        return new_entity.to_json()

    def delete_entity(self, entity_id: str) -> bool:
        """Delete a single entity from the context broker by its id.

        Args:
            entity_id (str): The id of an entity.

        Returns:
            bool: True if the entity was successfully deleted.
        """
        response = requests.delete(f"{self._entities_url}/{entity_id}")
        if response.ok:
            logger.info(f"Entity deleted: {entity_id}")
        else:
            logger.error(f"Error deleting entity {entity_id}"
                         f"{response.url}: {response.status_code} "
                         f"{response.text}")
        return response.ok
