from typing import List, Union, Optional
from datetime import datetime

class Subscription:
    """Class that represent a context broker subscription to one or more
    entities.

    Attributes:
        uri
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
    
    Properties:
        json (dict): The subscription as a JSON object.
    """

    def __init__(
        self,
        uri: str,
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
            uri (str): URI which conveys the endpoint which will
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
                "entity_type or watched_attributes must be provided "
                f"{entity_type}, {watched_attributes}"
            )

        if entity_type is not None:
            if isinstance(entity_type, str):
                entity_type = [entity_type]
        
        if entity_id is not None:
            if entity_type is None:
                raise ValueError(
                    "entity_type must be provided if entity_id is provided"
                )
            if isinstance(entity_id, str):
                entity_id = [entity_id]
            if len(entity_id) != len(entity_type):
                raise ValueError(
                    "entity_type and entity_id must have the same length "
                    f"{len(entity_type)}, {len(entity_id)}"
                )
        
        if entity_id_pattern is not None:
            if entity_type is None:
                raise ValueError(
                    "entity_type must be provided if entity_id_pattern is "
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
        self.uri = uri
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
                    "uri": self.uri,
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
        if self.query is not None:
            subscription["q"] = self.query
        
        # Add expiration
        if self.expires is not None:
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


