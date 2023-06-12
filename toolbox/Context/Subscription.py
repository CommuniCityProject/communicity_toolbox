from __future__ import annotations

import json as Json
from datetime import datetime
from typing import List, Optional, Union


class Subscription:
    """Class that represent a context broker subscription to one or more
    entities.

    Attributes:
        notification_uri
        subscription_id
        name
        description
        entity_type
        entity_id
        entity_id_pattern
        watched_attributes
        query
        notification_attributes
        notification_format
        notification_accept
        expires
        throttling

    Overloaded operators:
        __eq__
        __str__
    """

    def __init__(
        self,
        notification_uri: str,
        subscription_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        entity_type: Optional[Union[str, List[str]]] = None,
        entity_id: Optional[Union[str, List[str]]] = None,
        entity_id_pattern: Optional[Union[str, List[str]]] = None,
        watched_attributes: Optional[List[str]] = None,
        query: Optional[str] = None,
        notification_attributes: Optional[List[str]] = None,
        notification_format: str = "normalized",
        notification_accept: str = "application/json",
        expires: Optional[Union[str, datetime]] = None,
        throttling: Optional[int] = None,
    ):
        """Create a subscription object.

        Args:
            entity_type (Optional[Union[str, List[str]]]): Entity type to
                subscribe to. If None, `watched_attributes` must be provided.
                A single entity type or a list of entity types.
            notification_uri (str): URI which conveys the endpoint which will
                receive the notification.
            subscription_id (Optional[str], optional): Subscription ID. If
                None, a new one will be generated. Defaults to None.
            name (Optional[str], optional): A (short) name given to this
                Subscription. Defaults to None.
            description (Optional[str], optional): Subscription description.
                Defaults to None.
            entity_id (Optional[Union[str, List[str]]], optional): ID of the
                entity to subscribe or a list of entity IDs to subscribe to.
                If not provided, all entities of the given entity type will be
                subscribed. If used, `entity_id_pattern` must be None.
                Defaults to None.
            entity_id_pattern (Optional[Union[str, List[str]]], optional):
                A regular expression which denotes a pattern that shall be
                matched by the provided or subscribed Entities. A single or a
                list of expressions. If used, `entity_id` must be None.
                Defaults to None.
            watched_attributes (Optional[List[str]], optional): Watched
                Attributes (Properties or Relationships). If None, `entity_type`
                must be provided and all attributes will be watched.
                Defaults to None.
            query (Optional[str], optional): Query that shall be met by
                subscribed entities in order to trigger the notification.
                Defaults to None.
            notification_attributes (Optional[List[str]], optional): Entity
                Attribute Names (Properties or Relationships) to be included in
                the notification payload body. If None it will mean all
                Attributes. Defaults to None.
            notification_format (str, optional): Conveys the representation
                format of the entities delivered at notification time.
                "keyValues" or "normalized". Defaults to "normalized".
            notification_accept (str, optional): MIME type of the notification
                payload body ("application/json" or "application/ld+json").
                Defaults to "application/json".
            expires (Optional[Union[str, datetime]], optional): Expiration date
                for the subscription. datetime object or ISO 8601 String.
                Defaults to None.
            throttling (Optional[int], optional): Minimal period of time in
                seconds which shall elapse between two consecutive
                notifications. Defaults to None.

        Raises:
            ValueError: If the provided arguments are not valid.
        """

        # Preconditions and casting
        if entity_type is None and watched_attributes is None:
            raise ValueError(
                "entity_type or watched_attributes must be provided"
            )

        if entity_type is not None:
            if isinstance(entity_type, str):
                entity_type = [entity_type]

        if entity_id is not None:
            if entity_type is None:
                raise ValueError(
                    "entity_type can not be None if entity_id is provided"
                )
            if isinstance(entity_id, str):
                entity_id = [entity_id]
            if len(entity_id) != len(entity_type):
                raise ValueError(
                    "entity_type and entity_id must have the same length "
                    f"({len(entity_type)}, {len(entity_id)})"
                )

        if entity_id_pattern is not None:
            if entity_type is None:
                raise ValueError(
                    "entity_type can not be None if entity_id_pattern is "
                    "provided"
                )
            if isinstance(entity_id_pattern, str):
                entity_id_pattern = [entity_id_pattern]
            if len(entity_id_pattern) != len(entity_type):
                raise ValueError(
                    "entity_type and entity_id_pattern must have the same "
                    f"length {len(entity_type)}, {len(entity_id_pattern)})"
                )

        if isinstance(expires, datetime):
            expires = expires.strftime("%Y-%m-%dT%H:%M:%SZ")

        self.entity_type = entity_type
        self.notification_uri = notification_uri
        self.subscription_id = subscription_id
        self.name = name
        self.description = description
        self.entity_id = entity_id
        self.entity_id_pattern = entity_id_pattern
        self.watched_attributes = watched_attributes
        self.query = query
        self.notification_attributes = notification_attributes
        self.notification_format = notification_format
        self.notification_accept = notification_accept
        self.expires = expires
        self.throttling = throttling

    @property
    def json(self) -> dict:
        """Returns the subscription as a JSON object.
        """
        subscription = {
            "type": "Subscription",
            "notification": {
                "format": self.notification_format,
                "endpoint": {
                    "uri": self.notification_uri,
                    "accept": self.notification_accept
                }
            }
        }

        # Add notification attributes
        if self.notification_attributes is not None:
            subscription["notification"]["attributes"] = \
                self.notification_attributes

        # Add entities
        if self.entity_type is not None:
            subscription["entities"] = []
            for i, e_type in enumerate(self.entity_type):
                ent = {"type": e_type}
                if self.entity_id is not None and self.entity_id[i] is not None:
                    ent["id"] = self.entity_id[i]
                if self.entity_id_pattern is not None and \
                        self.entity_id_pattern[i] is not None:
                    ent["idPattern"] = self.entity_id_pattern[i]
                subscription["entities"].append(ent)

        # Add watched attributes
        if self.watched_attributes is not None:
            subscription["watchedAttributes"] = self.watched_attributes

        # Add query
        if self.query:
            subscription["q"] = self.query

        # Add expiration
        if self.expires:
            subscription["expires"] = self.expires

        # Add throttling
        if self.throttling is not None:
            subscription["throttling"] = self.throttling

        # Add description
        if self.description is not None:
            subscription["description"] = self.description

        # Add name
        if self.name is not None:
            subscription["name"] = self.name

        # Add subscription ID
        if self.subscription_id is not None:
            subscription["id"] = self.subscription_id

        return subscription

    @staticmethod
    def from_json(json: dict) -> Subscription:
        """Builds a subscription from a JSON.

        Args:
            json (dict): Subscription JSON dict.

        Returns:
            Subscription: A Subscription object.
        """
        # Check type
        if json.get("type", None) != "Subscription":
            raise ValueError("The provided JSON object is not a subscription")
        
        # Get ID
        subscription_id = json.get("id", None)

        # Get name
        name = json.get("subscriptionName", None)

        # Get description
        description = json.get("description", None)

        # Get entities
        if "entities" in json:
            entity_type = [ent["type"] for ent in json["entities"]]
            entity_id = [ent.get("id", None) for ent in json["entities"]]
            entity_id_pattern = [
                ent.get("idPattern", None)
                for ent in json["entities"]
            ]
            if set(entity_id) == {None}:
                entity_id = None
            if set(entity_id_pattern) == {None}:
                entity_id_pattern = None
        else:
            entity_type = None
            entity_id = None
            entity_id_pattern = None
            
        # Get watched_attributes
        watched_attributes = json.get("watchedAttributes", None)
        
        # Get query
        query = json.get("q", None)

        # Get notification
        notification = json["notification"]
        notification_attributes = notification.get("attributes", None)
        notification_format = notification.get("format", None)
        notification_accept = notification["endpoint"].get("accept", None)
        notification_uri = notification["endpoint"]["uri"]

        # Get expires
        expires = json.get("expires", None)

        # Get throttling
        throttling = json.get("throttling", None)

        return Subscription(
            notification_uri=notification_uri,
            subscription_id=subscription_id,
            name=name,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_id_pattern=entity_id_pattern,
            watched_attributes=watched_attributes,
            query=query,
            notification_attributes=notification_attributes,
            notification_format=notification_format,
            notification_accept=notification_accept,
            expires=expires,
            throttling=throttling
        )

    def __eq__(self, other: Subscription) -> bool:
        """Compares if two subscriptions are virtually equal.
        """
        if not isinstance(other, Subscription):
            return False

        # xor entity_type
        if (self.entity_type is None) != (other.entity_type is None):
            return False

        # xor entity_id
        if (self.entity_id is None) != (other.entity_id is None):
            return False

        # xor entity_id_pattern
        if (self.entity_id_pattern is None) != (other.entity_id_pattern is None):
            return False

        # Check entities
        if self.entity_type is not None:
            if len(self.entity_type) != len(other.entity_type):
                return False
            if set(self.entity_type) != set(other.entity_type):
                return False
        
        if self.entity_id is not None:
            if set(self.entity_id) != set(other.entity_id):
                return False
        
        if self.entity_id_pattern is not None:
            if set(self.entity_id_pattern) != set(other.entity_id_pattern):
                return False

        if self.watched_attributes != other.watched_attributes:
            return False
        if self.query != other.query:
            return False
        if self.notification_uri != other.notification_uri:
            return False
        if self.notification_format != other.notification_format:
            return False
        if self.notification_accept != other.notification_accept:
            return False
        if self.notification_attributes != other.notification_attributes:
            return False
        if self.expires != other.expires:
            return False
        if self.throttling != other.throttling:
            return False
        return True

    def __str__(self) -> str:
        """Returns the subscription as a JSON string.
        """
        return Json.dumps(self.json, indent=4)
    