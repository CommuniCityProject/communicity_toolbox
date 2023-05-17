import datetime
import unittest
from datetime import datetime

from toolbox.Context import Subscription


class TestSubscription(unittest.TestCase):

    def test_init(self):
        # Minimal args with entity_type
        sub = Subscription(
            notification_uri="host",
            entity_type="test"
        )
        self.assertEqual(sub.notification_uri, "host")
        self.assertEqual(sub.entity_type, ["test"])

        # Minimal args with watched_attribute
        sub = Subscription(
            notification_uri="host",
            watched_attributes=["test"]
        )
        self.assertEqual(sub.notification_uri, "host")
        self.assertEqual(sub.watched_attributes, ["test"])

        # No entity_type and watched_attribute
        with self.assertRaises(ValueError):
            Subscription(notification_uri="host")

        # Bad entity_id
        with self.assertRaises(ValueError):
            Subscription(notification_uri="host", entity_id="test")

        with self.assertRaises(ValueError):
            Subscription(
                notification_uri="host",
                entity_type=["1"],
                entity_id=["test", "test"]
            )

        # Bad entity_id_pattern
        with self.assertRaises(ValueError):
            Subscription(notification_uri="host", entity_id_pattern="test")

        with self.assertRaises(ValueError):
            Subscription(
                notification_uri="host",
                entity_type=["1"],
                entity_id_pattern=["test", "test"]
            )

        # Test list conversion
        sub = Subscription(
            notification_uri="host",
            entity_type="test",
            entity_id="test",
            entity_id_pattern="test",
        )
        self.assertEqual(sub.entity_type, ["test"])
        self.assertEqual(sub.entity_id, ["test"])
        self.assertEqual(sub.entity_id_pattern, ["test"])

        # Test datetime conversion
        sub = Subscription(
            notification_uri="host",
            entity_type="test",
            expires=datetime(2020, 1, 1, 0, 0, 0, 0)
        )
        self.assertEqual(sub.expires, "2020-01-01T00:00:00Z")

        # Full args
        sub = Subscription(
            notification_uri="notification",
            subscription_id="sub_id",
            name="a_name",
            description="a_description",
            entity_type="a_type",
            entity_id="a_id",
            entity_id_pattern="a_pattern",
            watched_attributes=["a1", "a2"],
            query="q==1",
            notification_attributes=["n1", "n2"],
            notification_format="keyValues",
            notification_accept="application/ld+json",
            expires=datetime(2020, 1, 1, 0, 0, 0, 0),
            throttling=5
        )

        self.assertEqual(sub.notification_uri, "notification")
        self.assertEqual(sub.subscription_id, "sub_id")
        self.assertEqual(sub.name, "a_name")
        self.assertEqual(sub.description, "a_description")
        self.assertEqual(sub.entity_type, ["a_type"])
        self.assertEqual(sub.entity_id, ["a_id"])
        self.assertEqual(sub.entity_id_pattern, ["a_pattern"])
        self.assertEqual(sub.watched_attributes, ["a1", "a2"])
        self.assertEqual(sub.query, "q==1")
        self.assertEqual(sub.notification_attributes, ["n1", "n2"])
        self.assertEqual(sub.notification_format, "keyValues")
        self.assertEqual(sub.notification_accept, "application/ld+json")
        self.assertEqual(sub.expires, "2020-01-01T00:00:00Z")
        self.assertEqual(sub.throttling, 5)

    def test_json(self):
        sub_args = {
            "notification_uri": "notification",
            "subscription_id": "sub_id",
            "name": "a_name",
            "description": "a_description",
            "entity_type": ["a_type", "a_type2"],
            "entity_id": ["a_id", "a_id2"],
            "watched_attributes": ["a1", "a2"],
            "query": "q==1",
            "notification_attributes": ["n1", "n2"],
            "notification_format": "keyValues",
            "notification_accept": "application/ld+json",
            "expires": datetime(2020, 1, 1, 0, 0, 0, 0),
            "throttling": 5
        }

        sub = Subscription(**sub_args)

        sub_json = sub.json
        self.assertEqual(sub_json["id"], sub_args["subscription_id"])
        self.assertEqual(sub_json["type"], "Subscription")
        self.assertEqual(sub_json["name"], sub_args["name"])
        self.assertEqual(sub_json["description"], sub_args["description"])
        self.assertEqual(sub_json["entities"][0]
                         ["type"], sub_args["entity_type"][0])
        self.assertEqual(sub_json["entities"][0]
                         ["id"], sub_args["entity_id"][0])
        self.assertEqual(sub_json["entities"][1]
                         ["type"], sub_args["entity_type"][1])
        self.assertEqual(sub_json["entities"][1]
                         ["id"], sub_args["entity_id"][1])
        self.assertEqual(sub_json["watchedAttributes"],
                         sub_args["watched_attributes"])
        self.assertEqual(sub_json["q"], sub_args["query"])
        self.assertEqual(
            sub_json["notification"]["attributes"], sub_args["notification_attributes"])
        self.assertEqual(sub_json["notification"]
                         ["format"], sub_args["notification_format"])
        self.assertEqual(sub_json["notification"]["endpoint"]
                         ["uri"], sub_args["notification_uri"])
        self.assertEqual(sub_json["notification"]["endpoint"]
                         ["accept"], sub_args["notification_accept"])
        self.assertEqual(sub_json["expires"], "2020-01-01T00:00:00Z")
        self.assertEqual(sub_json["throttling"], sub_args["throttling"])

        # Test entity_id and entity_id_pattern
        sub = Subscription(
            notification_uri="host",
            entity_type=["t1", "t2", "t3", "t4"],
            entity_id=[None, "id2", None, "id4"],
            entity_id_pattern=[None, None, "p3", "p4"]
        )
        sub_json = sub.json
        self.assertEqual(
            sub_json["entities"],
            [
                {"type": "t1"},
                {"type": "t2", "id": "id2"},
                {"type": "t3", "idPattern": "p3"},
                {"type": "t4", "id": "id4", "idPattern": "p4"}
            ]
        )

    def test_from_json(self):
        sub_json = {
            "id": "sub_id",
            "type": "Subscription",
            "subscriptionName": "a_name",
            "description": "a_description",
            "entities": [
                {"type": "t1"},
                {"type": "t2", "id": "id2"},
                {"type": "t3", "idPattern": "p3"},
                {"type": "t4", "id": "id4", "idPattern": "p4"}
            ],
            "watchedAttributes": ["a1", "a2"],
            "q": "q==1",
            "notification": {
                "attributes": ["n1", "n2"],
                "format": "keyValues",
                "endpoint": {
                    "uri": "host",
                    "accept": "application/ld+json"
                }
            },
            "expires": "2020-01-01T00:00:00Z",
            "throttling": 5
        }

        sub = Subscription.from_json(sub_json)

        self.assertEqual(sub.subscription_id, "sub_id")
        self.assertEqual(sub.name, "a_name")
        self.assertEqual(sub.description, "a_description")
        self.assertEqual(sub.entity_type, ["t1", "t2", "t3", "t4"])
        self.assertEqual(sub.entity_id, [None, "id2", None, "id4"])
        self.assertEqual(sub.entity_id_pattern, [None, None, "p3", "p4"])
        self.assertEqual(sub.watched_attributes, ["a1", "a2"])
        self.assertEqual(sub.query, "q==1")
        self.assertEqual(sub.notification_uri, "host")
        self.assertEqual(sub.notification_attributes, ["n1", "n2"])
        self.assertEqual(sub.notification_format, "keyValues")
        self.assertEqual(sub.notification_accept, "application/ld+json")
        self.assertEqual(sub.expires, "2020-01-01T00:00:00Z")
        self.assertEqual(sub.throttling, 5)

        # Test parse entities
        sub_json = {
            "type": "Subscription",
            "entities": [
                {"type": "t1"},
                {"type": "t2"},
                {"type": "t3"}
            ],
            "notification": {
                "format": "keyValues",
                "endpoint": {
                    "uri": "host",
                    "accept": "application/ld+json"
                }
            }
        }
        sub = Subscription.from_json(sub_json)
        self.assertEqual(sub.entity_type, ["t1", "t2", "t3"])
        self.assertEqual(sub.entity_id, None)
        self.assertEqual(sub.entity_id_pattern, None)
        
        sub_json["entities"] = [
            {"type": "t1"},
            {"type": "t2", "id": "id2"},
            {"type": "t3", "id": "id3"}
        ]
        sub = Subscription.from_json(sub_json)
        self.assertEqual(sub.entity_type, ["t1", "t2", "t3"])
        self.assertEqual(sub.entity_id, [None, "id2", "id3"])
        self.assertEqual(sub.entity_id_pattern, None)

        sub_json["entities"] = [
            {"type": "t1"},
            {"type": "t2", "idPattern": "p2"},
            {"type": "t3", "idPattern": "p3"}
        ]
        sub = Subscription.from_json(sub_json)
        self.assertEqual(sub.entity_type, ["t1", "t2", "t3"])
        self.assertEqual(sub.entity_id, None)
        self.assertEqual(sub.entity_id_pattern, [None, "p2", "p3"])

        sub_json["entities"] = [
            {"type": "t1"},
            {"type": "t2", "id": "id2", "idPattern": "p2"},
            {"type": "t3", "id": "id3", "idPattern": "p3"}
        ]
        sub = Subscription.from_json(sub_json)
        self.assertEqual(sub.entity_type, ["t1", "t2", "t3"])
        self.assertEqual(sub.entity_id, [None, "id2", "id3"])
        self.assertEqual(sub.entity_id_pattern, [None, "p2", "p3"])

        sub_json["entities"] = [
            {"type": "t1", "id": "id1", "idPattern": "p1"},
            {"type": "t2", "id": "id2", "idPattern": "p2"},
            {"type": "t3", "id": "id3", "idPattern": "p3"}
        ]
        sub = Subscription.from_json(sub_json)
        self.assertEqual(sub.entity_type, ["t1", "t2", "t3"])
        self.assertEqual(sub.entity_id, ["id1", "id2", "id3"])
        self.assertEqual(sub.entity_id_pattern, ["p1", "p2", "p3"])

    def test_eq(self):
        sub_args = {
            "notification_uri": "host",
            "subscription_id": "sub_id",
            "name": "a_name",
            "description": "a_description",
            "entity_type": ["a_type", "a_type2"],
            "entity_id": ["a_id", "a_id2"],
            "entity_id_pattern": ["a_pattern", "a_pattern2"],
            "watched_attributes": ["a1", "a2"],
            "query": "q==1",
            "notification_attributes": ["n1", "n2"],
            "notification_format": "keyValues",
            "notification_accept": "application/ld+json",
            "expires": datetime(2020, 1, 1, 0, 0, 0, 0),
            "throttling": 5
        }

        sub_1 = Subscription(**sub_args)

        args_cp = sub_args.copy()
        self.assertEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["notification_uri"] = "another"
        self.assertNotEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["subscription_id"] = "another"
        self.assertEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["name"] = "another"
        self.assertEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["description"] = "another"
        self.assertEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["entity_type"] = ["a_type", "a_type3"]
        self.assertNotEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["entity_id"] = ["a_id", "a_id3"]
        self.assertNotEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["entity_id_pattern"] = ["a_pattern", "a_pattern3"]
        self.assertNotEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["watched_attributes"] = ["a1", "a3"]
        self.assertNotEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["query"] = "q==2"
        self.assertNotEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["notification_attributes"] = ["n1", "n3"]
        self.assertNotEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["notification_format"] = "another"
        self.assertNotEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["notification_accept"] = "another"
        self.assertNotEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["expires"] = datetime(2020, 1, 2, 0, 0, 0, 0)
        self.assertNotEqual(sub_1, Subscription(**args_cp))

        args_cp = sub_args.copy()
        args_cp["throttling"] = 6
        self.assertNotEqual(sub_1, Subscription(**args_cp))

        sub_1 = Subscription(
            notification_uri="host",
            watched_attributes=["a1"],
        )
        self.assertEqual(sub_1, sub_1)
        self.assertNotEqual(
            sub_1,
            Subscription(
                notification_uri="host",
                entity_type=["a_type"],
            )
        )

        self.assertNotEqual(
            Subscription(
                notification_uri="host",
                entity_type=["a_type"],
            ),
            Subscription(
                notification_uri="host",
                entity_type=["a_type"],
                entity_id=["a_id"],
            )
        )

        self.assertNotEqual(
            Subscription(
                notification_uri="host",
                entity_type=["a_type"],
            ),
            Subscription(
                notification_uri="host",
                entity_type=["a_type"],
                entity_id_pattern=["a_id"],
            )
        )


if __name__ == "__main__":
    unittest.main()
