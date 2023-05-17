from typing import List, Type, Union, Optional, Iterator
import uuid
import requests
import copy
import itertools

from toolbox.DataModels import BaseModel
from toolbox.Context import entity_parser
from .Subscription import Subscription
from toolbox.DataModels.DataModelsCatalog import data_models_catalog
from toolbox.utils.utils import get_logger, urljoin


logger = get_logger("toolbox.ContextConsumer")


class ContextConsumer:
    """Manage the consumption of context data from a context broker.

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
        parse_entity(entity_id) -> Type[BaseModel]
        parse_dict(entity) -> Type[BaseModel]

    Static Methods:
        subscription_equals(sub_a, sub_b) -> bool

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
        """Initialize the ContextConsumer.

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
    ) -> Union[str, None]:
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

        Returns:
            str: The subscription id or None if the subscription could not be
                created.
        """
        if subscription is None:
            subscription = self._build_subscription(**kwargs)

        if self._check_subscription_conflicts:
            conflicts = self.get_conflicting_subscriptions(subscription)
            if conflicts:
                logger.warning(f"Found {len(conflicts)} conflicting "
                               f"subscription: {conflicts}. "
                               "Not creating the subscription.")
                return conflicts[0].subscription_id

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
                return None
        logger.error(f"Error creating subscription {subscription} at "
                     f"{response.url}: {response.status_code} {response.text}")
        return None

    def get_subscription(
        self,
        subscription_id: str
    ) -> Union[Subscription, None]:
        """Get a subscription from the context broker by its id.

        Args:
            subscription_id (str): Subscription id.

        Returns:
            Union[Subscription, None]: The Subscription object or None if the
                subscription could not be found.
        """
        url = urljoin(self._subscriptions_uri, subscription_id)
        logger.debug(f"Getting subscription from {url}")
        response = requests.get(url)
        if response.ok:
            return Subscription.from_json(response.json())
        logger.error(f"Error getting subscription from {url}: "
                     f"{response.status_code} {response.text}")
        return None

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

        Returns:
            List[Subscription]: List of Subscription objects.
        """
        url = urljoin(self._subscriptions_uri, f"?limit={limit}&offset={offset}")
        logger.debug(f"Getting subscriptions from {url}")
        response = requests.get(url)
        if response.ok:
            return [Subscription.from_json(s) for s in response.json()]
        logger.error(f"Error getting subscriptions from {url}: "
                     f"{response.status_code} {response.text}")
        return []

    def iterate_subscriptions(
        self,
        limit: int = 100
    ) -> Iterator[List[Subscription]]:
        """Iterate over the current subscriptions in the context broker.

        Args:
            limit (int, optional): Maximum number of subscriptions to return
                in each iteration. Defaults to 100.

        Yields:
            Iterator[List[Subscription]]: Iterator over the subscriptions.
        """
        offset = 0
        while True:
            try:
                subs = self.get_subscriptions_page(limit, offset)
                if not subs:
                    break
                yield subs
                offset += limit
            except Exception as e:
                logger.exception(
                    f"Error iterating over subscriptions: {e}",
                    exc_info=True
                )
                break

    def get_all_subscriptions(self) -> List[Subscription]:
        """Get all the current subscriptions in the context broker.

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

        Returns:
            List[Subscription]: A list with the conflicting subscriptions.
        """
        return [s for s in self.get_all_subscriptions() if s == subscription]

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
            r = self.unsubscribe(sub_id) and r
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
