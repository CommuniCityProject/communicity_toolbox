from typing import List, Type, Union, Optional, Iterator
import uuid
import requests
import copy
import itertools

from toolbox.DataModels import BaseModel
from toolbox.Context import entity_parser
from toolbox.DataModels.DataModelsCatalog import data_models_catalog
from toolbox.utils.utils import get_logger

logger = get_logger("toolbox.ContextConsumer")


class ContextConsumer:
    """Manage the consumption of context data from a context broker.

    Attributes:
        notification_uri (str): The uri used for notifications.
        subscription_name (str): The name used in subscriptions.

    Methods:
        build_subscription(entity_type, uri) -> dict
        subscribe(subscription) -> Union[str, None]
        get_subscription(subscription_id) -> Union[dict, None]
        get_subscriptions(limit, offset) -> List[dict]
        iterate_subscriptions(limit) -> Iterator[dict]
        get_all_subscriptions() -> List[dict]
        get_conflicting_subscriptions(subscription) -> List[dict]
        unsubscribe(subscription_id) -> bool
        unsubscribe_all() -> bool
        parse_entity(entity_id) -> Type[BaseModel]
        parse_dict(entity) -> Type[BaseModel]

    Static Methods:
        subscription_equals(sub_a, sub_b) -> bool

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
        self.notification_uri = config["context_broker"].get(
            "notification_uri", None)
        self._check_subscription_conflicts = config["context_broker"].get(
            "check_subscription_conflicts", False)
        self.subscription_name = str(uuid.uuid4())
        self._subscription_ids: List[str] = []
        logger.info(f"Using context broker at {self._broker_url}")

    def build_subscription(
        self,
        entity_type: str,
        uri: Optional[str] = None,
        subscription_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        entity_id: Optional[str] = None,
        entity_id_pattern: Optional[str] = None,
        watched_attributes: Optional[List[str]] = None,
        query: Optional[str] = None,
        notification_attributes: Optional[List[str]] = None,
        notification_format: str = "normalized",
        notification_accept: str = "application/json",
        expires: Optional[str] = None,
        throttling: Optional[int] = None,
    ) -> dict:
        """Create a dict with the subscription data that can be posted to the
        context broker.

        Args:
            entity_type (str): Entity type to subscribe to.
            uri (Optional[str]): URI which conveys the endpoint which will
                receive the notification. If None, the `notification_uri`
                attribute of the ContextConsumer will be used. Defaults to
                None.
            subscription_id (Optional[str], optional): Subscription ID. If
                None, a new one will be generated. Defaults to None.
            name (Optional[str], optional): A (short) name given to this
                Subscription. If None, the `subscription_name` attribute of the
                ContextConsumer will be used. Defaults to None.
            description (Optional[str], optional): Subscription description.
                Defaults to None.
            entity_id (Optional[str], optional): ID of the entity to subscribe
                to. Defaults to None.
            entity_id_pattern (Optional[str], optional): A regular expression
                which denotes a pattern that shall be matched by the provided
                or subscribed Entities. Defaults to None.
            watched_attributes (Optional[List[str]], optional): Watched
                Attributes (Properties or Relationships). If None it means any
                Attribute. Defaults to None.
            query (Optional[str], optional): Query that shall be met by
                subscribed entities in order to trigger the notification.
                Defaults to None.
            notification_attributes (Optional[List[str]], optional): Entity
                Attribute Names (Properties or Relationships) to be included in
                the notification payload body. If None it will mean all
                Attributes. Defaults to None.
            notification_format (str, optional): Conveys the representation
                format of the entities delivered at notification time. By
                default,it will be in normalized format. Defaults to
                "normalized".
            notification_accept (str, optional): MIME type of the notification
                payload body (``application/json`` or ``application/ld+json``).
                Defaults to "application/json".
            expires (Optional[str], optional): Expiration date for the
                subscription. ISO 8601 String. Defaults to None.
            throttling (Optional[int], optional): Minimal period of time in
                seconds which shall elapse between two consecutive
                notifications. Defaults to None.

        Returns:
            dict: The subscription data as a dict.
        """
        if uri is None:
            uri = self.notification_uri

        if name is None:
            name = self.subscription_name
            
        subscription_data = {
            "type": "Subscription",
            "name": name,
            "entities": [{"type": entity_type}],
            "notification": {
                "format": notification_format,
                "endpoint": {
                    "uri": uri,
                    "accept": notification_accept
                }
            }
        }
        if subscription_id is not None:
            subscription_data["id"] = subscription_id
        if description is not None:
            subscription_data["description"] = description
        if entity_id is not None:
            subscription_data["entities"][0]["id"] = entity_id
        if entity_id_pattern is not None:
            subscription_data["entities"][0]["idPattern"] = entity_id_pattern
        if watched_attributes is not None:
            subscription_data["watchedAttributes"] = watched_attributes
        if query is not None:
            subscription_data["q"] = query
        if notification_attributes is not None:
            subscription_data["notification"]["attributes"] = notification_attributes
        if expires is not None:
            subscription_data["expires"] = expires
        if throttling is not None:
            subscription_data["throttling"] = throttling
        return subscription_data

    def subscribe(self, subscription: Optional[dict] = None,
                  **kwargs) -> Union[str, None]:
        """Create a subscription in the context broker.

        Args:
            subscription (Optional[dict]): The subscription data as a dict (see
                :meth:`build_subscription`). If None, the subscription data
                will be built from the kwargs. Defaults to None.
            kwargs: The subscription data as keyword arguments (see
                :meth:`build_subscription`). If subscription is not None, the
                kwargs will be ignored. Defaults to None.

        Returns:
            str: The subscription id.
        """
        if subscription is None:
            subscription = self.build_subscription(**kwargs)

        if self._check_subscription_conflicts:
            conflicts = self.get_conflicting_subscriptions(subscription)
            if conflicts:
                logger.warning(f"Found {len(conflicts)} conflicting "
                               f"subscription: {conflicts}."
                               "Not creating the subscription.")
                return conflicts[0]["id"]

        response = requests.post(
            url=self._subscriptions_uri,
            json=subscription,
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
                return None
        logger.error(f"Error creating subscription {subscription} at "
                     f"{response.url}: {response.status_code} {response.text}")
        return None

    def get_subscription(self, subscription_id: str) -> Union[dict, None]:
        """Get a subscription from the context broker by its id.

        Args:
            subscription_id (str): Subscription id.

        Returns:
            Union[dict, None]: The subscription data as a dict or None if the
                subscription does not exist.
        """
        url = f"{self._subscriptions_uri}/{subscription_id}"
        logger.debug(f"Getting subscription from {url}")
        response = requests.get(url)
        if response.ok:
            return response.json()
        logger.error(f"Error getting subscription from {url}: "
                     f"{response.status_code} {response.text}")
        return None

    def get_subscriptions(self, limit: int = 100, offset: int = 0
                          ) -> List[dict]:
        """Get the current subscriptions in the context broker.

        Args:
            limit (int, optional): Maximum number of subscriptions to return.
                Maximum value is 1000. Defaults to 100.
            offset (int, optional): Pagination offset. Defaults to 0.

        Returns:
            List[dict]: List of JSONs with the subscriptions.
        """
        url = f"{self._subscriptions_uri}/?limit={limit}&offset={offset}"
        logger.debug(f"Getting subscriptions from {url}")
        response = requests.get(url)
        if response.ok:
            return response.json()
        logger.error(f"Error getting subscriptions from {url}: "
                     f"{response.status_code} {response.text}")
        return []

    def iterate_subscriptions(self, limit: int = 100) -> Iterator[List[dict]]:
        """Iterate over the current subscriptions in the context broker.

        Args:
            limit (int, optional): Maximum number of subscriptions to return
                in each iteration. Defaults to 100.

        Yields:
            Iterator[List[dict]]: Iterator over the subscriptions.
        """
        offset = 0
        while True:
            try:
                subs = self.get_subscriptions(limit, offset)
                if not subs:
                    break
                yield subs
                offset += limit
            except:
                break

    def get_all_subscriptions(self) -> List[dict]:
        """Get all the current subscriptions in the context broker.

        Returns:
            List[dict]: List of the subscriptions in the context broker.
        """
        return list(
            itertools.chain.from_iterable(self.iterate_subscriptions(1000))
        )

    @staticmethod
    def subscription_equals(sub_a: dict, sub_b: dict) -> bool:
        """Check if two subscriptions are virtually the same.

        Args:
            sub_a (dict): Subscription data as a dict (see
                :meth:`build_subscription`).
            sub_b (dict): Subscription data as a dict (see
                :meth:`build_subscription`).

        Returns:
            bool: True if the subscriptions are virtually the same, False
                otherwise.
        """
        if len(sub_a["entities"]) > len(sub_b["entities"]):
            max_e = sub_a["entities"]
            min_e = sub_b["entities"]
        else:
            max_e = sub_b["entities"]
            min_e = sub_a["entities"]
        for e in max_e:
            if e not in min_e:
                return False
        if sub_a.get("watchedAttributes") != sub_b.get("watchedAttributes"):
            return False
        if sub_a.get("q") != sub_b.get("q"):
            return False
        if sub_a["notification"]["format"] != sub_b["notification"]["format"]:
            return False
        if sub_a["notification"]["endpoint"] != \
                sub_b["notification"]["endpoint"]:
            return False
        if sub_a["notification"].get("attributes") != \
                sub_b["notification"].get("attributes"):
            return False
        if sub_a.get("expires") != sub_b.get("expires"):
            return False
        if sub_a.get("throttling") != sub_b.get("throttling"):
            return False
        return True

    def get_conflicting_subscriptions(self, subscription: dict) -> List[dict]:
        """Get a list of subscriptions in the context broker that are virtually
        the same as the given subscription.

        Args:
            subscription (dict): The subscription data as a dict (see
                :meth:`build_subscription`).

        Returns:
            List[dict]: A list with the conflicting subscriptions.
        """
        broker_subs = self.get_all_subscriptions()
        conflicts = []
        for broker_sub in broker_subs:
            if self.subscription_equals(subscription, broker_sub):
                conflicts.append(broker_sub)
        return conflicts

    def unsubscribe(self, subscription_id: str) -> bool:
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
            url=f"{self._subscriptions_uri}/{subscription_id}"
        )
        if response.ok:
            logger.info(f"Subscription deleted: {subscription_id}")
        else:
            logger.error(
                f"Error deleting subscription {subscription_id} from "
                f"{response.url}: {response.status_code} {response.text}"
            )
        return response.ok

    def unsubscribe_all(self) -> bool:
        """Delete all the subscriptions created within the ContextConsumer.

        Returns:
            bool: True if all the subscriptions were deleted successfully.
        """
        r = True
        for sub_id in reversed(self._subscription_ids):
            r = self._unsubscribe(sub_id) and r
        return r

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
            raise KeyError(f"Entity type {entity_type} not registered" +
                           f" in data models catalog {data_models_catalog}")
        data_model_cls = data_models_catalog[entity_type]
        return entity_parser.parse_entity(entity, data_model_cls)

    @property
    def subscription_ids(self) -> List[str]:
        return copy.copy(self._subscription_ids)
