from typing import List, Type, Union, Optional
import uuid
import requests
import copy

from toolbox.DataModels import BaseModel
from toolbox.Context import entity_parser
from toolbox.DataModels.DataModelsCatalog import data_models_catalog
from toolbox.utils.utils import get_logger

logger = get_logger("toolbox.ContextConsumer")



class ContextConsumer:
    """Manage the consumption of context data from a context broker.

    Attributes:
        subscription_name (str): The name used in subscriptions.

    Methods:
        subscribe(entity_type, watched_attributes, query) -> Union[str, None]
        unsubscribe(subscription_id) -> bool
        parse_entity(entity_id) -> Union[Type[BaseModel], None]
        parse_dict(entity) -> Type[BaseModel]
        get_subscriptions() -> List[dict]
        subscription_conflicts(entity_type, watched_attributes, query) -> List[dict]
    
    Properties (read-only):
        subscription_ids (List[str]): List of ids of the created subscriptions.
    """
    
    def __init__(self, config: dict):
        """Initialize the ContextConsumer.

        Args:
            config (dict): Configuration dictionary.
        """
        self._broker_host = config["context_broker"]["host"]
        self._broker_port = config["context_broker"]["port"]
        self._broker_url = f"http://{self._broker_host}:{self._broker_port}"
        self._subscriptions_uri = f"{self._broker_url}/ngsi-ld/v1/subscriptions"
        self._entities_uri = f"{self._broker_url}/ngsi-ld/v1/entities"
        self._notification_uri = config["context_broker"].get(
            "notification_uri", None)
        self._check_subscription_conflicts = config["context_broker"].get(
            "check_subscription_conflicts", False)
        self.subscription_name = str(uuid.uuid4())
        self._subscription_ids: List[str] = []
        logger.info(f"Using context broker at {self._broker_url}")

    def _build_subscription_dict(self, subscription_name: str,
        notification_uri: str, entity_type: str,
        watched_attributes: List[str], query: str) -> dict:
        """Create a dict with the subscription data that can be posted to the
        context broker.

        Args:
            subscription_name (str): Subscription name.
            notification_uri (str): Notification uri.
            entity_type (str): Entity type.
            watched_attributes (List[str]): List of watched attributes.
            query (str): Subscription query.

        Returns:
            dict: The subscription data as a dict.
        """
        assert isinstance(watched_attributes, list), watched_attributes
        assert isinstance(query, str), query
        subscription_data = {
            "type": "Subscription",
            "name": subscription_name,
            "entities": [{"type": entity_type}],
            "notification": {
                "format": "normalized", # "keyValues" | "normalized"
                "endpoint": {
                    "uri": notification_uri,
                    "accept": "application/json"
                },
            }
        }
        if watched_attributes:
            subscription_data["watchedAttributes"] = watched_attributes
        if query:
            subscription_data["q"] = query
        return subscription_data
        
    def subscribe(self, entity_type: str, watched_attributes: List[str] = [],
        query: str = "") -> Union[str, None]:
        """Create a subscription to the context broker.

        Args:
            entity_type (str): The type of entity to watch.
            watched_attributes (List[str], optional): List of entity attributes
                to watch. Defaults to [].
            query (str, optional): A query to filter. Defaults to "".

        Returns:
            str: The subscription id.
        """
        assert self._notification_uri is not None
        
        if self._check_subscription_conflicts:
            conflicts = self.subscription_conflicts(
                entity_type, watched_attributes, query)
            if conflicts:
                logger.warning(f"Found {len(conflicts)} conflicting " \
                    f"subscription: {conflicts}; Not creating the subscription")
                return conflicts[0]["id"]

        subscription_data = self._build_subscription_dict(
            self.subscription_name,
            self._notification_uri,
            entity_type,
            watched_attributes,
            query
        )

        response = requests.post(
            url = self._subscriptions_uri,
            json = subscription_data,
            headers = {
                "Accept": "application/ld+json",
                "Content-Type": "application/json",
            }
        )

        if response.ok:
            try:
                location = response.headers.get("Location")
                sub_id = location.rsplit("/", 1)[-1]
                self._subscription_ids.append(sub_id)
                logger.info(f"Subscription created: {sub_id}")
                return sub_id
            except Exception as e:
                logger.error(e)
        logger.error(f"Error creating subscription {subscription_data}" \
            f"{response.url}: {response.status_code} {response.text}")
        return None

    def get_subscriptions(self) -> List[dict]:
        """Get a list of all the current subscriptions in the context broker.

        Returns:
            List[dict]: List of the subscriptions in the context broker.
        """
        limit = 1000
        offset = 0
        subscriptions = []
        while True:
            response = requests.get(
                f"{self._subscriptions_uri}/?limit={limit}&offset={offset}"
            )
            if response.ok:
                batch = response.json()
                if not batch:
                    break
                subscriptions += batch
                offset += limit
            else:
                break
        return subscriptions

    def subscription_conflicts(self, entity_type: str,
        watched_attributes: List[str] = [], query: str = "") -> List[dict]:
        """Check if the creation of a subscription will conflict with any other
        in the context broker.

        Args:
            entity_type (str): The type of entity to watch.
            watched_attributes (List[str], optional): List of entity attributes
                to watch. Defaults to [].
            query (str, optional): A query to filter. Defaults to "".

        Returns:
            List[str]: A list with the conflicting subscriptions.
        """
        def _get_comp_sub(sub: dict) -> dict:
            return  {
                "type": sub.get("type", ""),
                "entities": sub.get("entities", ""),
                "watchedAttributes": sub.get("watchedAttributes", []),
                "q": sub.get("q", ""),
                "format": sub.get("notification", {}).get("format", ""),
                "endpoint": sub.get("notification", {}).get("endpoint", ""),
            }

        subscription_data = self._build_subscription_dict(
            self.subscription_name,
            self._notification_uri,
            entity_type,
            watched_attributes,
            query
        )
        comp_sub = _get_comp_sub(subscription_data)

        broker_subs = self.get_subscriptions()
        conflicts = []
        for broker_sub in broker_subs:
            comp_broker_sub = _get_comp_sub(broker_sub)
            if comp_sub == comp_broker_sub:
                conflicts.append(broker_sub)
        return conflicts
    
    def _unsubscribe(self, subscription_id: str) -> bool:
        """Delete a subscription from the context broker.

        Args:
            subscription_id (Optional[str]): The id of the subscription to
                delete.
        
        Returns:
            bool: True if success.
        """
        if subscription_id in self._subscription_ids:
            self._subscription_ids.remove(subscription_id)
        response = requests.delete(
            url = f"{self._subscriptions_uri}/{subscription_id}"
        )
        if response.ok:
            logger.info(f"Subscription deleted: {subscription_id}")
        else:
            logger.error(f"Error deleting subscription {subscription_id}" \
                f"{response.url}: {response.status_code} {response.text}")
        return response.ok

    def unsubscribe(self, subscription_id:  Optional[str] = None) -> bool:
        """Delete a subscription from the context broker.

        Args:
            subscription_id (Optional[str]): The id of the subscription to
                delete or None to delete all subscriptions created within
                the ContextConsumer.
        
        Returns:
            bool: True if success.
        """
        if subscription_id is None:
            r = True
            for sub_id in reversed(self._subscription_ids):
                r = self._unsubscribe(sub_id) and r
            return r
        else:
            return self._unsubscribe(subscription_id)

    def parse_entity(self, entity_id: str) -> Type[BaseModel]:
        """Retrieve an entity from the context broker by its id and convert
        it to toolbox data model.

        Args:
            entity_id (str): The id of an entity.
        
        Raises:
            KeyError: If the entity type is not recognized.
            ValueError: If the entity can not be retrieved.

        Returns:
            Type[BaseModel]: A data model object.
        """
        response = requests.get(f"{self._entities_uri}/{entity_id}")

        if response.ok:
            entity = response.json()
            return self.parse_dict(entity)
        
        raise ValueError(f"Could not retrieve entity '{entity_id}'")
    
    def parse_dict(self, entity: dict) -> Type[BaseModel]:
        """Parse an entity from a dict and return a toolbox data model.

        Args:
            entity (dict): An entity.

        Raises:
            KeyError: If the entity type is not recognized.

        Returns:
            Type[BaseModel]: A data model.
        """
        entity_type = entity["type"]
        if entity_type not in data_models_catalog:
            raise KeyError(f"Entity type {entity_type} not registered" + \
                f" in data models catalog {data_models_catalog}")
        data_model_cls = data_models_catalog[entity_type]
        return entity_parser.parse_entity(entity, data_model_cls)

    @property
    def subscription_ids(self) -> List[str]:
        return copy.copy(self._subscription_ids)
    