import copy
import itertools
import json
import logging
import uuid
from datetime import datetime
from typing import Iterator, List, Optional, Type, Union

import requests
from ngsildclient import Client as NgsiLdClient

from toolbox import DataModels
from toolbox.Context import entity_parser
from toolbox.DataModels import BaseModel
from toolbox.DataModels.DataModelsCatalog import data_models_catalog
from toolbox.utils.utils import get_logger, urljoin

from .entity_parser import create_entity
from .Subscription import Subscription

logger = get_logger("toolbox.ContextCli")
logging.getLogger("ngsildclient").setLevel(logging.WARNING)


class ContextCli:
    """A client for managing common operations on a context broker.

    Attributes:
        notification_uri (str): The uri used for notifications.
        subscription_name (str): The name used in subscriptions.

    Methods:
        subscribe(subscription, **kwargs) -> Union[str, None]
        get_subscription(subscription_id) -> Union[Subscription, None]
        get_subscriptions_page(limit, offset) -> List[Subscription]
        iterate_subscriptions(limit) -> Iterator[Subscription]
        get_all_subscriptions() -> List[Subscription]
        get_conflicting_subscriptions(subscription) -> List[Subscription]
        unsubscribe(subscription_id) -> bool
        unsubscribe_all() -> bool
        get_entity(entity_id) -> dict
        get_data_model(entity_id) -> Type[BaseModel]
        parse_data_model(entity) -> Type[BaseModel]
        post_entity(entity)
        post_data_model(data_model) -> dict
        delete_entity(entity_id) -> bool

    Properties (read-only):
        subscription_ids (List[str]): List of ids of the created subscriptions.
    """

    def __init__(
        self,
        host: str,
        port: int,
        base_path: str = "",
        notification_uri: str = None,
        check_subscription_conflicts: bool = False
    ):
        """Initialize the ContextCli.

        Args:
            host (str): Host address of the context broker.
            port (int): Port of the context broker.
            base_path (str, optional): URL path to the context broker.
                Defaults to "".
            notification_uri (str, optional): The uri used for the
                subscriptions notifications. Defaults to None.
            check_subscription_conflicts (bool, optional): If True, the
                subscription will be checked for conflicts before being
                created. Defaults to False.
        """
        self._broker_host = host
        self._broker_port = port
        self._base_path = base_path
        self.notification_uri = notification_uri
        self._check_subscription_conflicts = check_subscription_conflicts

        self._subscription_ids: List[str] = []
        self.subscription_name = str(uuid.uuid4())

        self._broker_url = urljoin(
            f"http://{self._broker_host}:{self._broker_port}",
            base_path
        )
        self._subscriptions_uri = urljoin(
            self._broker_url,
            "/ngsi-ld/v1/subscriptions"
        )
        self._entities_uri = urljoin(
            self._broker_url,
            "/ngsi-ld/v1/entities"
        )

        logger.info(f"Using context broker at {self._broker_url}")

    def _build_subscription(self, **kwargs) -> Subscription:
        """Create a Subscription object from the given kwargs.
        If "notification_uri" is not provided, the `notification_uri` attribute
        will be used. If "name" is not provided, the `subscription_name`
        attribute will be used.

        Returns:
            Subscription: The Subscription object.
        """
        if "notification_uri" not in kwargs:
            kwargs["notification_uri"] = self.notification_uri
        if "name" not in kwargs:
            kwargs["name"] = self.subscription_name
        subscription = Subscription(**kwargs)
        return subscription

    def subscribe(
        self,
        subscription: Optional[Subscription] = None,
        **kwargs
    ) -> str:
        """Create a subscription in the context broker from a Subscription
        object or from the given kwargs.

        Args:
            subscription (Optional[Subscription]): A Subscription object.
                If None, a Subscription will be built from the kwargs.
                Defaults to None.
            kwargs: The subscription data as keyword arguments (see 
                :class:`Subscription` for the list of valid arguments). If
                subscription is not None, the kwargs will be ignored.
                Defaults to None.

        Raises:
            requests.exceptions.HTTPError: If the subscription could not be
                created.
            Exception: If there was an error creating the subscription.

        Returns:
            str: The subscription id.
        """
        if subscription is None:
            subscription = self._build_subscription(**kwargs)

        if self._check_subscription_conflicts:
            conflicts = self.get_conflicting_subscriptions(subscription)
            if conflicts:
                logger.warning(f"Found {len(conflicts)} conflicting "
                               "subscription: "
                               f"{[c.subscription_id for c in conflicts]}. "
                               "Not creating the subscription.")
                return conflicts[0].subscription_id

        logger.debug(f"Creating subscription {subscription}")
        response = requests.post(
            url=self._subscriptions_uri,
            json=subscription.json,
            headers={
                "Accept": "application/ld+json",
                "Content-Type": "application/json",
            }
        )

        if response.ok:
            try:
                location = response.headers.get("Location")
                sub_id = location.rsplit("/", 1)[-1]
                self._subscription_ids.append(sub_id)
                logger.info(f"Subscription created with ID: {sub_id}")
                return sub_id
            except Exception as e:
                logger.exception(
                    f"Error creating subscription {subscription}: {e}",
                    exc_info=True
                )
                raise e
        logger.error(f"Error creating subscription {subscription} at "
                     f"{response.url}: {response.status_code} {response.text}")
        response.raise_for_status()

    def get_subscription(
        self,
        subscription_id: str
    ) -> Union[Subscription, None]:
        """Get a subscription from the context broker by its id.

        Args:
            subscription_id (str): Subscription id.

        Raises:
            requests.exceptions.HTTPError: If there was an error getting the
                subscription.

        Returns:
            Union[Subscription, None]: The retrieved Subscription object or
                None if the subscription was not found.
        """
        url = urljoin(self._subscriptions_uri, subscription_id)
        logger.debug(f"Getting subscription from {url}")
        response = requests.get(url)
        if response.ok:
            return Subscription.from_json(response.json())
        elif response.status_code == 404:
            return None
        logger.error(f"Error getting subscription from {url}: "
                     f"{response.status_code} {response.text}")
        response.raise_for_status()

    def get_subscriptions_page(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Subscription]:
        """Get a list of subscriptions in the context broker.

        Args:
            limit (int, optional): Maximum number of subscriptions to return.
                Maximum value is 1000. Defaults to 100.
            offset (int, optional): Pagination offset. Defaults to 0.

        Raises:
            requests.exceptions.HTTPError: If the subscriptions could not be
                retrieved successfully.

        Returns:
            List[Subscription]: List of Subscription objects.
        """
        params = {"limit": limit, "offset": offset}
        logger.debug(f"Getting subscriptions from {self._subscriptions_uri} "
                     f"with params {params}")
        response = requests.get(self._subscriptions_uri, params=params)
        if response.ok:
            return [Subscription.from_json(s) for s in response.json()]
        logger.error(f"Error getting subscriptions from f"{response.url}: "
                     f"{response.status_code} {response.text}")
        response.raise_for_status()

    def iterate_subscriptions(
        self,
        limit: int = 100
    ) -> Iterator[List[Subscription]]:
        """Iterate over the current subscriptions in the context broker.

        Args:
            limit (int, optional): Maximum number of subscriptions to return
                in each iteration. Defaults to 100.

        Raises:
            requests.exceptions.HTTPError: If the subscriptions could not be
                retrieved successfully.

        Yields:
            Iterator[List[Subscription]]: Iterator over the subscriptions.
        """
        offset = 0
        while True:
            subs = self.get_subscriptions_page(limit, offset)
            if not subs:
                break
            yield subs
            offset += limit

    def get_all_subscriptions(self) -> List[Subscription]:
        """Get all the current subscriptions in the context broker.

        Raises:
            requests.exceptions.HTTPError: If the subscriptions could not be
                retrieved successfully.

        Returns:
            List[Subscription]: List of the subscriptions in the context broker.
        """
        return list(
            itertools.chain.from_iterable(self.iterate_subscriptions(1000))
        )

    def get_conflicting_subscriptions(
        self,
        subscription: Subscription
    ) -> List[Subscription]:
        """Get a list of subscriptions in the context broker that are virtually
        the same as the given subscription.

        Args:
            subscription (dict): A subscription object.

        Raises:
            requests.exceptions.HTTPError: If the subscriptions could not be
                retrieved successfully.

        Returns:
            List[Subscription]: A list with the conflicting subscriptions.
        """
        return [s for s in self.get_all_subscriptions() if s == subscription]

    def unsubscribe(self, subscription_id: str) -> bool:
        """Delete a subscription from the context broker.

        Args:
            subscription_id (Optional[str]): The id of the subscription to
                delete.

        Raises:
            requests.exceptions.HTTPError: If there was an error deleting the
                subscription.

        Returns:
            bool: True if success.
        """
        if subscription_id in self._subscription_ids:
            self._subscription_ids.remove(subscription_id)
        response = requests.delete(
            url=urljoin(self._subscriptions_uri, subscription_id)
        )
        if response.ok:
            logger.info(f"Subscription deleted {subscription_id}")
            return True
        if response.status_code == 404:
            return False
        logger.error(
            f"Error deleting subscription {subscription_id} from "
            f"{response.url}: {response.status_code} {response.text}"
        )
        response.raise_for_status()

    def unsubscribe_all(self) -> bool:
        """Delete all the subscriptions created within the ContextCli.

        Raises:
            requests.exceptions.HTTPError: If the subscriptions could not be
                retrieved successfully.

        Returns:
            bool: True if all the subscriptions were deleted successfully.
        """
        r = True
        for sub_id in reversed(self._subscription_ids):
            r = self.unsubscribe(sub_id) and r
        return r

    def get_entity(
        self,
        entity_id: str,
        as_dict: bool = False
    ) -> Union[Type[BaseModel], dict, None]:
        """Retrieve an entity from the context broker by its ID.

        Args:
            entity_id (str): The ID of an entity.
            as_dict (bool, optional): If True, the entity will be returned as
                a dictionary. Otherwise, it will be converted to a toolbox
                data model. Defaults to False.

        Raises:
            requests.exceptions.HTTPError: If there was an error getting the
                entity.
            KeyError: If the entity type is not recognized and as_dict is
                False.

        Returns:
            Union[Type[BaseModel], dict, None]: A data model object, a
                dictionary or None if the entity does not exist.
        """
        logger.debug(f"Getting entity {entity_id}")
        response = requests.get(urljoin(self._entities_uri, entity_id))
        if response.ok:
            entity_dict = response.json()
            if as_dict:
                return entity_dict
            return self.parse_data_model(entity_dict)
        if response.status_code == 404:
            return None
        logger.error(f"Error getting entity {entity_id} from {response.url}: "
                     f"{response.status_code} {response.text}")
        response.raise_for_status()

    def get_entities_page(
        self,
        entity_id: Optional[List[str]] = None,
        entity_type: Optional[str] = None,
        id_pattern: Optional[str] = None,
        attrs: Optional[List[str]] = None,
        query: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        as_dict: bool = False
    ) -> List[Union[Type[BaseModel], dict]]:
        """Get a list of entities from the context broker.

        Args:
            entity_id (Optional[List[str]], optional): A list of entity IDs.
                Defaults to None.
            entity_type (Optional[str], optional): An entity type. If not
                provided, attrs must be provided. Defaults to None. 
            id_pattern (Optional[str], optional): A pattern to match entity
                IDs. Defaults to None.
            attrs (Optional[List[str]], optional): A list of attributes to
                return. If not provided, entity_type must be provided.
                Defaults to None.
            query (Optional[str], optional): A query to filter entities.
                Defaults to None.
            limit (int, optional): Maximum number of entities to return.
                Maximum value is 1000. Defaults to 100.
            offset (int, optional): Pagination offset. Defaults to 0.
            as_dict (bool, optional): If True, the entities will be returned as
                dictionaries. Otherwise, they will be converted to a toolbox
                data model. Defaults to False.

        Raises:
            requests.exceptions.HTTPError: If there was an error getting the
                entities.
            KeyError: If the entity type is not recognized and as_dict is
                False.

        Returns:
            List[Union[Type[BaseModel], dict]]: A list of data model objects or
                dictionaries.
        """
        params = {"limit": limit, "offset": offset}
        if entity_id:
            params["id"] = ",".join(entity_id)
        if entity_type:
            params["type"] = entity_type
        if id_pattern:
            params["idPattern"] = id_pattern
        if attrs:
            params["attrs"] = ",".join(attrs)
        if query:
            params["q"] = query
        logger.debug(f"Getting entities from {self._entities_uri} with "
                     f"params {params}")
        response = requests.get(self._entities_uri, params=params)
        if response.ok:
            entity_dicts = response.json()
            if as_dict:
                return entity_dicts
            return [self.parse_data_model(e) for e in entity_dicts]
        logger.error(f"Error getting entities from {response.url}: "
                     f"{response.status_code} {response.text}")
        response.raise_for_status()

    def iterate_entities(
        self,
        entity_id: Optional[List[str]] = None,
        entity_type: Optional[str] = None,
        id_pattern: Optional[str] = None,
        attrs: Optional[List[str]] = None,
        query: Optional[str] = None,
        limit: int = 100,
        as_dict: bool = False
    ) -> Iterator[List[Union[Type[BaseModel], dict]]]:
        """Iterate through a list of entities from the context broker.

        Args:
            entity_id (Optional[List[str]], optional): A list of entity IDs.
                Defaults to None.
            entity_type (Optional[str], optional): An entity type. If not
                provided, attrs must be provided. Defaults to None. 
            id_pattern (Optional[str], optional): A pattern to match entity
                IDs. Defaults to None.
            attrs (Optional[List[str]], optional): A list of attributes to
                return. If not provided, entity_type must be provided.
                Defaults to None.
            query (Optional[str], optional): A query to filter entities.
                Defaults to None.
            limit (int, optional): Maximum number of entities to return in each
                iteration. Maximum value is 1000. Defaults to 100.
            as_dict (bool, optional): If True, the entities will be returned as
                dictionaries. Otherwise, they will be converted to a toolbox
                data model. Defaults to False.

        Raises:
            requests.exceptions.HTTPError: If there was an error getting the
                entities.
            KeyError: If the entity type is not recognized and as_dict is
                False.

        Returns:
            Iterator[List[Union[Type[BaseModel], dict]]]: An iterator of data
                model objects or dictionaries.
        """
        offset = 0
        while True:
            entities = self.get_entities_page(
                entity_id=entity_id,
                entity_type=entity_type,
                id_pattern=id_pattern,
                attrs=attrs,
                query=query,
                limit=limit,
                offset=offset,
                as_dict=as_dict
            )
            if not entities:
                break
            yield entities
            offset += limit
    
    def get_all_entities(
        self,
        entity_id: Optional[List[str]] = None,
        entity_type: Optional[str] = None,
        id_pattern: Optional[str] = None,
        attrs: Optional[List[str]] = None,
        query: Optional[str] = None,
        as_dict: bool = False
    ) -> List[Union[Type[BaseModel], dict]]:
        """Get all entities from the context broker.

        Args:
            entity_id (Optional[List[str]], optional): A list of entity IDs.
                Defaults to None.
            entity_type (Optional[str], optional): An entity type. If not
                provided, attrs must be provided. Defaults to None. 
            id_pattern (Optional[str], optional): A pattern to match entity
                IDs. Defaults to None.
            attrs (Optional[List[str]], optional): A list of attributes to
                return. If not provided, entity_type must be provided.
                Defaults to None.
            query (Optional[str], optional): A query to filter entities.
                Defaults to None.
            as_dict (bool, optional): If True, the entities will be returned as
                dictionaries. Otherwise, they will be converted to a toolbox
                data model. Defaults to False.

        Raises:
            requests.exceptions.HTTPError: If there was an error getting the
                entities.
            KeyError: If the entity type is not recognized and as_dict is
                False.

        Returns:
            List[Union[Type[BaseModel], dict]]: A list of data model objects or
                dictionaries.
        """
        return list(
            itertools.chain.from_iterable(
                self.iterate_entities(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    id_pattern=id_pattern,
                    attrs=attrs,
                    query=query,
                    as_dict=as_dict,
                    limit=1000
                )
            )
        )

    def parse_data_model(self, entity: dict) -> Type[BaseModel]:
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
        return entity_parser.parse_entity(entity, data_model_cls)

    @property
    def subscription_ids(self) -> List[str]:
        """Get the list of subscription IDs created within the ContextCli.
        """
        return copy.copy(self._subscription_ids)

    def post_json(self, entity: dict):
        """Post a JSON entity to the context broker.

        Args:
            entity (dict): The entity to upload to the context broker as a
                JSON dictionary.

        Raises:
            requests.exceptions.HTTPError: If there was an error posting the
                entity.
        """
        logger.debug(f"Posting entity to the context broker: \n{entity}")
        response = requests.post(
            self._entities_uri,
            json=entity
        )
        if not response.ok:
            logger.error(f"Error posting entity to {response.url}: "
                         f"{response.status_code} {response.text}")
            response.raise_for_status()

    def post_data_model(self, data_model: Type[DataModels.BaseModel]) -> dict:
        """Post a toolbox data model object to the context broker. If the data
        model ID is None, a new one will be assigned.

        Args:
            data_model (Type[DataModels.BaseModel]): The data model object to
                upload to the context broker.

        Returns:
            dict: The uploaded JSON.
        """
        logger.debug(f"Posting data model to the context broker: "
                     f"\n{data_model.pretty()}")
        entity = create_entity(data_model)
        entity.tprop("dateModified", datetime.now())
        entity.tprop("dateCreated", datetime.now())
        with NgsiLdClient(self._broker_host, self._broker_port) as cli:
            cli.create(entity)
            return json.loads(entity.to_json())
    
    def update_data_model(
        self,
        data_model: Type[DataModels.BaseModel],
        create: bool = False
    ) -> dict:
        """Update an existing entity in the context broker.

        Args:
            data_model (Type[DataModels.BaseModel]): The data model to update.
            create (bool): If the entity should be created if it does not
                exists. Defaults to False.

        Raises:
            ValueError: If the ID of the data model is None.
            ngsildclient.api.exceptions.NgsiResourceNotFoundError: If the data
                model does not exist on the context broker and  `create` is
                False.

        Returns:
            dict: The uploaded json.
        """
        logger.debug(f"Updating data model: \n{data_model.pretty()}")
        with NgsiLdClient(self._broker_host, self._broker_port) as cli:
            if create:
                if data_model.id is None or not cli.exists(data_model.id):
                    logger.debug(
                        "Data model does not exist on the context broker")
                    self.post_data_model(data_model)
                    return
            if data_model.id is None:
                raise ValueError("Can not update entity with ID None")
            orig_entity = self._broker.get(data_model.id)
            new_entity = create_entity(data_model)
            if "dateCreated" in orig_entity.to_dict():
                created = orig_entity["dateCreated"]["value"]["@value"]
                new_entity.tprop("dateCreated", created)
            new_entity.tprop("dateModified", datetime.now())
            self._broker.update(new_entity)
            return new_entity.to_json()

    @staticmethod
    def data_model_to_dict(data_model: Type[DataModels.BaseModel]) -> dict:
        """Convert a toolbox data model object to a dictionary.

        Args:
            data_model (Type[DataModels.BaseModel]): The data model object to
                convert.

        Returns:
            dict: The converted dictionary.
        """
        entity = create_entity(data_model)
        entity.tprop("dateModified", datetime.now())
        entity.tprop("dateCreated", datetime.now())
        return json.loads(entity.to_json())

    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity from the context broker.

        Args:
            entity_id (str): The ID of the entity to delete.

        Raises:
            requests.exceptions.HTTPError: If there was an error deleting
                the entity.

        Returns:
            bool: True if success.
        """
        response = requests.delete(urljoin(self._entities_uri, entity_id))
        if response.ok:
            logger.info(f"Entity deleted {entity_id}")
            return True
        if response.status_code == 404:
            return False
        logger.error(f"Error deleting entity {entity_id} from "
                        f"{response.url}: {response.status_code} "
                        f"{response.text}")
        response.raise_for_status()