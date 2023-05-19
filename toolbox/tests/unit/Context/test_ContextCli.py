import datetime
import json
import pathlib
import unittest
import uuid

import requests

from toolbox import DataModels
from toolbox.Context import ContextCli, Subscription
from toolbox.Structures import BoundingBox, Emotion, Gender
from toolbox.utils.config_utils import parse_config
from toolbox.utils.utils import urljoin

p = pathlib.Path(__file__).parent.resolve()
config = parse_config(p/"config.yaml")["context_broker"]
_context_broker_uri = urljoin(
    f"http://{config['host']}:{config['port']}", config["base_path"])
_entities_uri = urljoin(_context_broker_uri, "/ngsi-ld/v1/entities")
_subscriptions_uri = urljoin(_context_broker_uri, "/ngsi-ld/v1/subscriptions")


class TestContextCli(unittest.TestCase):

    def test_init(self):
        cc = ContextCli(**config)
        self.assertEqual(cc.notification_uri, config["notification_uri"])
        self.assertTrue(cc.subscription_name)

    def test_subscribe(self):
        cc = ContextCli(**config)

        # Test with given ID
        s_id = "urn:ngsi-ld:Subscription:" + str(uuid.uuid4())
        sub = Subscription(
            notification_uri="http://1.2.3.4:5678",
            entity_type="Ty",
            subscription_id=s_id
        )
        id_0 = cc.subscribe(sub)
        self.assertEqual(id_0, s_id)
        self.assertEqual(cc.subscription_ids[0], id_0)

        # Test from a subscription object
        sub = Subscription(
            notification_uri="http://1.2.3.4:5678",
            entity_type="Ty"
        )
        id_1 = cc.subscribe(sub)
        self.assertTrue(id_1.startswith("urn:"))
        self.assertEqual(cc.subscription_ids[1], id_1)

        # Test from args
        id_2 = cc.subscribe(
            notification_uri="http://1.2.3.4:5678",
            entity_type="Ty"
        )
        self.assertTrue(id_2.startswith("urn:"))
        self.assertEqual(cc.subscription_ids[2], id_2)

        id_3 = cc.subscribe(
            notification_uri="http://1.2.3.4:5678",
            name="a_name",
            description="a_description",
            entity_type="Ty",
            entity_id="urn:ngsi-ld:Ty:123",
            # entity_id_pattern="urn:ngsi-ld:Ty:.*",
            watched_attributes=["a1", "a2"],
            query="a1==true",
            notification_attributes=["b1", "b2"],
            notification_format="keyValues",
            notification_accept="application/ld+json",
            expires="2021-01-01T00:00:00Z",
            throttling=5,
        )
        self.assertTrue(id_3.startswith("urn:"))
        self.assertEqual(cc.subscription_ids[3], id_3)

        # Get the subscription from the context broker
        r = requests.get(urljoin(_subscriptions_uri, id_3))
        self.assertTrue(r.ok)
        ret_sub = r.json()
        self.assertEqual(ret_sub["id"], id_3)
        self.assertEqual(ret_sub["type"], "Subscription")
        self.assertEqual(ret_sub["subscriptionName"], "a_name")
        self.assertEqual(ret_sub["description"], "a_description")
        self.assertEqual(ret_sub["entities"], [
                         {"type": "Ty", "id": "urn:ngsi-ld:Ty:123"}])
        self.assertEqual(ret_sub["watchedAttributes"], ["a1", "a2"])
        self.assertEqual(ret_sub["q"], "a1==true")
        self.assertEqual(ret_sub["notification"]["attributes"], ["b1", "b2"])
        self.assertEqual(ret_sub["notification"]["format"], "keyValues")
        self.assertEqual(ret_sub["notification"]
                         ["endpoint"]["uri"], "http://1.2.3.4:5678")
        self.assertEqual(ret_sub["notification"]
                         ["endpoint"]["accept"], "application/ld+json")
        self.assertEqual(ret_sub["expiresAt"], "2021-01-01T00:00:00.000Z")
        self.assertEqual(ret_sub["throttling"], 5)

        # Test without name and notification_uri
        id_4 = cc.subscribe(entity_type="Ty")
        r = requests.get(urljoin(_subscriptions_uri, id_4))
        ret_sub = r.json()
        self.assertEqual(ret_sub["subscriptionName"], cc.subscription_name)
        self.assertEqual(ret_sub["notification"]
                         ["endpoint"]["uri"], cc.notification_uri)

        # Test check conflicts
        config_2 = config.copy()
        config_2["check_subscription_conflicts"] = True
        cc = ContextCli(**config_2)
        id_5 = cc.subscribe(entity_type="Ty")
        id_6 = cc.subscribe(entity_type="Ty")
        self.assertEqual(id_5, id_6)

    def test_get_subscription(self):
        cc = ContextCli(**config)
        s_id = cc.subscribe(
            notification_uri="http://1.2.3.4:5678",
            name="a_name",
            description="a_description",
            entity_type="Ty",
            entity_id="urn:ngsi-ld:Ty:123",
            # entity_id_pattern="urn:ngsi-ld:Ty:.*",    # Only one of entity_id and entity_id_pattern can be used
            watched_attributes=["a1", "a2"],
            query="a1==true",
            notification_attributes=["b1", "b2"],
            notification_format="keyValues",
            notification_accept="application/ld+json",
            # expires="2021-01-01T00:00:00Z",    # Not supported by the context broker
            throttling=5,
        )
        sub = cc.get_subscription(s_id)
        self.assertIsInstance(sub, Subscription)
        self.assertEqual(sub.subscription_id, s_id)
        self.assertEqual(sub.notification_uri, "http://1.2.3.4:5678")
        self.assertEqual(sub.name, "a_name")
        self.assertEqual(sub.description, "a_description")
        self.assertEqual(sub.entity_type, ["Ty"])
        self.assertEqual(sub.entity_id, ["urn:ngsi-ld:Ty:123"])
        self.assertEqual(sub.watched_attributes, ["a1", "a2"])
        self.assertEqual(sub.query, "a1==true")
        self.assertEqual(sub.notification_attributes, ["b1", "b2"])
        self.assertEqual(sub.notification_format, "keyValues")
        self.assertEqual(sub.notification_accept, "application/ld+json")
        self.assertEqual(sub.throttling, 5)

        sub = cc.get_subscription("none")
        self.assertIsNone(sub)

    def test_get_subscriptions_page(self):
        cc = ContextCli(**config)
        for _ in range(6):
            cc.subscribe(entity_type="Ty")
        subs_0 = cc.get_subscriptions_page(3, 0)
        subs_1 = cc.get_subscriptions_page(3, 1)
        self.assertIsInstance(subs_0, list)
        self.assertIsInstance(subs_1, list)
        self.assertIsInstance(subs_0[0], Subscription)
        self.assertIsInstance(subs_1[0], Subscription)
        self.assertEqual(len(subs_0), 3)
        self.assertEqual(len(subs_1), 3)
        self.assertEqual(subs_0[1].subscription_id, subs_1[0].subscription_id)
        self.assertEqual(subs_0[2].subscription_id, subs_1[1].subscription_id)
        self.assertNotEqual(subs_0[0].subscription_id,
                            subs_1[2].subscription_id)

    def test_iterate_subscriptions(self):
        cc = ContextCli(**config)
        for _ in range(6):
            cc.subscribe(entity_type="Ty")
        it = cc.iterate_subscriptions(3)
        subs_0 = next(it)
        subs_1 = next(it)
        self.assertIsInstance(subs_0, list)
        self.assertIsInstance(subs_1, list)
        self.assertIsInstance(subs_0[0], Subscription)
        self.assertIsInstance(subs_1[0], Subscription)
        self.assertEqual(len(subs_0), 3)
        self.assertEqual(len(subs_1), 3)
        set_0 = set([s.subscription_id for s in subs_0])
        set_1 = set([s.subscription_id for s in subs_1])
        self.assertEqual(len(set_0), 3)
        self.assertEqual(len(set_1), 3)
        self.assertEqual(len(set_0.intersection(set_1)), 0)

    def test_get_all_subscriptions(self):
        cc = ContextCli(**config)
        pre_subs = cc.get_all_subscriptions()
        self.assertIsInstance(pre_subs, list)
        self.assertIsInstance(pre_subs[0], Subscription)
        for _ in range(6):
            s_id = cc.subscribe(entity_type="Ty")
        post_subs = cc.get_all_subscriptions()
        self.assertEqual(len(pre_subs) + 6, len(post_subs))
        self.assertIn(s_id, set([s.subscription_id for s in post_subs]))

    def test_get_conflicting_subscriptions(self):
        cc = ContextCli(**config)
        t = str(uuid.uuid4())
        id_0 = cc.subscribe(
            entity_type=[t, t],
            entity_id=["urn:ngsi-ld:Ty:123", "urn:ngsi-ld:Ty:456"],
            query="a1==true"
        )
        conflicts = cc.get_conflicting_subscriptions(
            Subscription(
                name=cc.subscription_name,
                notification_uri=cc.notification_uri,
                entity_type=[t, t],
                entity_id=["urn:ngsi-ld:Ty:123", "urn:ngsi-ld:Ty:456"],
                query="a1==true"
            )
        )
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].subscription_id, id_0)

        id_1 = cc.subscribe(
            entity_type=[t, t],
            entity_id=["urn:ngsi-ld:Ty:123", "urn:ngsi-ld:Ty:456"],
            query="a1==true"
        )
        conflicts = cc.get_conflicting_subscriptions(
            Subscription(
                name="a_name",
                notification_uri=cc.notification_uri,
                entity_type=[t, t],
                entity_id=["urn:ngsi-ld:Ty:123", "urn:ngsi-ld:Ty:456"],
                query="a1==true"
            )
        )
        self.assertEqual(len(conflicts), 2)

        conflicts = cc.get_conflicting_subscriptions(
            Subscription(
                notification_uri=cc.notification_uri,
                entity_type=[t, "t"],
                entity_id=["urn:ngsi-ld:Ty:123", "urn:ngsi-ld:Ty:456"],
                query="a1==true"
            )
        )
        self.assertEqual(len(conflicts), 0)

    def test_unsubscribe(self):
        cc = ContextCli(**config)

        total_subs_0 = len(cc.get_all_subscriptions())

        # Make 4 subscriptions
        s_id0 = cc.subscribe(entity_type="T0")
        s_id1 = cc.subscribe(entity_type="T1")
        s_id2 = cc.subscribe(entity_type="T2")
        s_id3 = cc.subscribe(entity_type="T3")

        self.assertIn(s_id0, cc.subscription_ids)
        self.assertIn(s_id1, cc.subscription_ids)
        self.assertIn(s_id2, cc.subscription_ids)
        self.assertIn(s_id3, cc.subscription_ids)

        total_subs_1 = len(cc.get_all_subscriptions())
        self.assertEqual(total_subs_0 + 4, total_subs_1)
        self.assertEqual(len(cc.subscription_ids), 4)

        # Unsubscribe 0
        self.assertTrue(cc.unsubscribe(s_id0))
        self.assertEqual(len(cc.subscription_ids), 3)
        self.assertNotIn(s_id0, cc.subscription_ids)
        self.assertEqual(total_subs_1-1, len(cc.get_all_subscriptions()))

        # Unsubscribe 0 again
        self.assertFalse(cc.unsubscribe(s_id0))
        self.assertEqual(len(cc.subscription_ids), 3)
        self.assertEqual(total_subs_1-1, len(cc.get_all_subscriptions()))

        # Unsubscribe non-existent
        self.assertFalse(cc.unsubscribe(
            "urn:ngsi-ld:Subscription:non-existent"))
        self.assertEqual(len(cc.subscription_ids), 3)
        self.assertEqual(total_subs_1-1, len(cc.get_all_subscriptions()))

        # Unsubscribe 3
        self.assertTrue(cc.unsubscribe(s_id3))
        self.assertEqual(len(cc.subscription_ids), 2)
        self.assertNotIn(s_id3, cc.subscription_ids)
        self.assertEqual(total_subs_1-2, len(cc.get_all_subscriptions()))

    def test_unsubscribe_all(self):
        cc = ContextCli(**config)

        total_subs_0 = len(cc.get_all_subscriptions())

        # Make 4 subscriptions
        s_id0 = cc.subscribe(entity_type="T0")
        s_id1 = cc.subscribe(entity_type="T1")
        s_id2 = cc.subscribe(entity_type="T2")
        s_id3 = cc.subscribe(entity_type="T3")

        total_subs_1 = len(cc.get_all_subscriptions())
        self.assertEqual(total_subs_0 + 4, total_subs_1)
        self.assertEqual(len(cc.subscription_ids), 4)

        cc.unsubscribe_all()
        self.assertEqual(len(cc.subscription_ids), 0)
        self.assertEqual(total_subs_0, len(cc.get_all_subscriptions()))

    def test_get_entity(self):
        cc = ContextCli(**config)

        e_id = "urn:ngsi-ld:Test:" + str(uuid.uuid4())

        # Post an entity to the broker
        r = requests.post(
            _entities_uri,
            headers={"Content-Type": "application/ld+json"},
            data=json.dumps({
                "id": e_id,
                "type": "Test",
                "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"],
                "test_prop": {"type": "Property", "value": "test_val"}
            })
        )

        # Get the entity from the broker
        e = cc.get_entity(e_id, as_dict=True)
        self.assertEqual(e["id"], e_id)
        self.assertEqual(e["type"], "Test")
        self.assertEqual(e["test_prop"]["value"], "test_val")

        # Post a toolbox data model entity to the broker
        e_id = "urn:ngsi-ld:Face:" + str(uuid.uuid4())
        e_type = "Face"
        context = ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]
        date_observed = "2000-01-01T00:00:00Z"
        image = "urn:ngsi-ld:Image:123"
        bounding_box = {"xmin": 0.0, "ymin": 0.1, "xmax": 0.2, "ymax": 0.3}
        detection_confidence = 0.99
        age = 30.5
        gender = "FEMALE"
        gender_confidence = 0.88
        emotion = "HAPPINESS"
        emotion_confidence = 0.77
        features = [1.1, 2.2, 3.3]
        features_algorithm = "algorithm"
        recognition_domain = "domain"
        recognized = False
        recognized_distance = 2.2
        recognized_person = "person"

        # Post it to the broker
        r = requests.post(
            _entities_uri,
            headers={"Content-Type": "application/ld+json"},
            data=json.dumps({
                "id": e_id,
                "type": e_type,
                "@context": context,
                "dateObserved": {"type": "Property", "value": {"@type": "DateTime", "@value": date_observed}},
                "image": {"type": "Relationship", "object": image},
                "boundingBox": {"type": "Property", "value": bounding_box},
                "detectionConfidence": {"type": "Property", "value": detection_confidence},
                "age": {"type": "Property", "value": age},
                "gender": {"type": "Property", "value": gender},
                "genderConfidence": {"type": "Property", "value": gender_confidence},
                "emotion": {"type": "Property", "value": emotion},
                "emotionConfidence": {"type": "Property", "value": emotion_confidence},
                "features": {"type": "Property", "value": features},
                "featuresAlgorithm": {"type": "Property", "value": features_algorithm},
                "recognitionDomain": {"type": "Property", "value": recognition_domain},
                "recognized": {"type": "Property", "value": recognized},
                "recognizedDistance": {"type": "Property", "value": recognized_distance},
                "recognizedPerson": {"type": "Property", "value": recognized_person}
            })
        )

        # Retrieve the data model by its ID
        ret_dm = cc.get_entity(e_id)
        self.assertIsInstance(ret_dm, DataModels.Face)
        self.assertEqual(e_id, ret_dm.id)
        self.assertEqual(e_type, ret_dm.type)
        self.assertEqual(datetime.datetime.fromisoformat(
            date_observed[:-1]), ret_dm.dateObserved)
        self.assertEqual(image, ret_dm.image)
        self.assertEqual(BoundingBox(bounding_box["xmin"], bounding_box["ymin"], bounding_box["xmax"], bounding_box["ymax"]),
                         ret_dm.bounding_box)
        self.assertEqual(detection_confidence, ret_dm.detection_confidence)
        self.assertEqual(age, ret_dm.age)
        self.assertEqual(Gender[gender], ret_dm.gender)
        self.assertEqual(gender_confidence, ret_dm.gender_confidence)
        self.assertEqual(Emotion[emotion], ret_dm.emotion)
        self.assertEqual(emotion_confidence, ret_dm.emotion_confidence)
        self.assertEqual(features, ret_dm.features)
        self.assertEqual(features_algorithm, ret_dm.features_algorithm)
        self.assertEqual(recognition_domain, ret_dm.recognition_domain)
        self.assertEqual(recognized, ret_dm.recognized)
        self.assertEqual(recognized_distance, ret_dm.recognized_distance)
        self.assertEqual(recognized_person, ret_dm.recognized_person)
        ret_dm = cc.get_entity(e_id, as_dict=True)
        self.assertEqual(ret_dm["@context"], context[0])
        
        # Get non-existing entities
        self.assertIsNone(cc.get_entity("urn:ngsi-ld:Face:non-existing"))
        self.assertIsNone(cc.get_entity("non-existing"))
        self.assertIsNone(cc.get_entity(""))

    def test_get_entities_page(self):
        cc = ContextCli(**config)
        # Create dummy entities
        test_type = str(uuid.uuid4())
        ids = ["urn:ngsi-ld:Test:" + str(uuid.uuid4()) for _ in range(11)]
        prop1 = ("test_prop_1" + test_type)
        entity = {
            "type": test_type,
            prop1: {"type": "Property", "value": "test_val_1"},
            "test_prop_2": {"type": "Property", "value": "test_val_2"}
        }
        for e_id in ids:
            entity["id"] = e_id
            r = requests.post(_entities_uri, json=entity)
            self.assertEqual(r.status_code, 201, msg=r.text)
        
        # Get by type
        entities = cc.get_entities_page(entity_type=test_type, limit=11, offset=0, as_dict=True)
        self.assertEqual(len(entities), 11)
        for e_id, e in zip(ids, entities):
            self.assertEqual(e_id, e["id"])
        
        entities_0 = cc.get_entities_page(entity_type=test_type, limit=5, offset=0, as_dict=True)
        entities_1 = cc.get_entities_page(entity_type=test_type, limit=5, offset=5, as_dict=True)
        entities_2 = cc.get_entities_page(entity_type=test_type, limit=5, offset=10, as_dict=True)
        self.assertEqual(len(entities_0), 5)
        self.assertEqual(len(entities_1), 5)
        self.assertEqual(len(entities_2), 1)
        for e_id, e in zip(ids[:5], entities_0):
            self.assertEqual(e_id, e["id"])
        for e_id, e in zip(ids[5:10], entities_1):
            self.assertEqual(e_id, e["id"])
        for e_id, e in zip(ids[10:], entities_2):
            self.assertEqual(e_id, e["id"])

        # Get by attrs
        entities = cc.get_entities_page(attrs=[prop1], limit=11, offset=0, as_dict=True)
        self.assertEqual(len(entities), 11)
        for e_id, e in zip(ids, entities):
            self.assertEqual(e_id, e["id"])

        # Get by entity_id
        entities = cc.get_entities_page(entity_id=ids, limit=11, offset=0, as_dict=True)
        self.assertEqual(len(entities), 11)
        for e_id, e in zip(ids, entities):
            self.assertEqual(e_id, e["id"])
        
        # Get by id_pattern
        entities = cc.get_entities_page(id_pattern=ids[-1][:-1]+"*", limit=11, offset=0, as_dict=True)
        self.assertEqual(len(entities), 1)
        self.assertEqual(ids[-1], entities[0]["id"])

        # Get by query
        entities = cc.get_entities_page(
            query=f'{prop1}=="test_val_1"', limit=11, offset=0, as_dict=True)
        self.assertEqual(len(entities), 11)
        for e_id, e in zip(ids, entities):
            self.assertEqual(e_id, e["id"])
        
        # Get none
        entities = cc.get_entities_page(entity_type="non-existing", limit=11, offset=0, as_dict=True)
        self.assertEqual(len(entities), 0)
        
        # Get data model
        e_id = "urn:ngsi-ld:Face:" + str(uuid.uuid4())
        e_type = "Face"
        context = ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]
        date_observed = "2000-01-01T00:00:00Z"
        image = "urn:ngsi-ld:Image:123"
        bounding_box = {"xmin": 0.0, "ymin": 0.1, "xmax": 0.2, "ymax": 0.3}
        detection_confidence = 0.99

        # Post it to the broker
        r = requests.post(
            _entities_uri,
            headers={"Content-Type": "application/ld+json"},
            data=json.dumps({
                "id": e_id,
                "type": e_type,
                "@context": context,
                "dateObserved": {"type": "Property", "value": {"@type": "DateTime", "@value": date_observed}},
                "image": {"type": "Relationship", "object": image},
                "boundingBox": {"type": "Property", "value": bounding_box},
                "detectionConfidence": {"type": "Property", "value": detection_confidence},
            })
        )

        # Retrieve the data model by its ID
        entities = cc.get_entities_page(entity_id=e_id, limit=11, offset=0)
        self.assertEqual(len(entities), 1)
        ret_dm = entities[0]
        self.assertIsInstance(ret_dm, DataModels.Face)
        self.assertEqual(e_id, ret_dm.id)
        self.assertEqual(e_type, ret_dm.type)
        self.assertEqual(image, ret_dm.image)
        self.assertEqual(BoundingBox(bounding_box["xmin"], bounding_box["ymin"], bounding_box["xmax"], bounding_box["ymax"]),
                         ret_dm.bounding_box)
        self.assertEqual(detection_confidence, ret_dm.detection_confidence)
    
        entities = cc.get_entities_page(entity_id=e_id, limit=11, offset=0, as_dict=True)
        self.assertEqual(entities[0]["@context"], context[0])

    def test_iterate_entities(self):
        cc = ContextCli(**config)
        # Create dummy entities
        test_type = str(uuid.uuid4())
        ids = ["urn:ngsi-ld:Test:" + str(uuid.uuid4()) for _ in range(11)]
        entity = {
            "type": test_type,
            "test_prop": {"type": "Property", "value": "test_val"}
        }
        for e_id in ids:
            entity["id"] = e_id
            r = requests.post(_entities_uri, json=entity)
            self.assertEqual(r.status_code, 201, msg=r.text)
        
        # Iterate over entities
        it = cc.iterate_entities(entity_type=test_type, limit=5, as_dict=True)
        ent_0 = next(it)
        ent_1 = next(it)
        ent_2 = next(it)
        with self.assertRaises(StopIteration):
            ent_3 = next(it)
        self.assertEqual(len(ent_0), 5)
        self.assertEqual(len(ent_1), 5)
        self.assertEqual(len(ent_2), 1)
        for e_id, e in zip(ids[:5], ent_0):
            self.assertEqual(e_id, e["id"])
        for e_id, e in zip(ids[5:10], ent_1):
            self.assertEqual(e_id, e["id"])
        self.assertEqual(ids[10], ent_2[0]["id"])

    def test_get_all_entities(self):
        cc = ContextCli(**config)
        # Create dummy entities
        test_type = str(uuid.uuid4())
        ids = ["urn:ngsi-ld:Test:" + str(uuid.uuid4()) for _ in range(11)]
        entity = {
            "type": test_type,
            "test_prop": {"type": "Property", "value": "test_val"}
        }
        for e_id in ids:
            entity["id"] = e_id
            r = requests.post(_entities_uri, json=entity)
            self.assertEqual(r.status_code, 201, msg=r.text)
        # Get all entities
        entities = cc.get_all_entities(entity_type=test_type, as_dict=True)
        self.assertEqual(len(entities), 11)
        for e_id, e in zip(ids, entities):
            self.assertEqual(e_id, e["id"])
        
        # Use toolbox data model
        static_rand_id = "urn:ngsi-ld:Face:" + str(uuid.uuid4())
        ids = [static_rand_id + str(uuid.uuid4()) for _ in range(3)]
        e_type = "Face"
        context = ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]
        date_observed = "2000-01-01T00:00:00Z"
        image = "urn:ngsi-ld:Image:123"
        bounding_box = {"xmin": 0.0, "ymin": 0.1, "xmax": 0.2, "ymax": 0.3}
        detection_confidence = 0.99

        # Post it to the broker
        for e_id in ids:
            r = requests.post(
                _entities_uri,
                headers={"Content-Type": "application/ld+json"},
                data=json.dumps({
                    "id": e_id,
                    "type": e_type,
                    "@context": context,
                    "dateObserved": {"type": "Property", "value": {"@type": "DateTime", "@value": date_observed}},
                    "image": {"type": "Relationship", "object": image},
                    "boundingBox": {"type": "Property", "value": bounding_box},
                    "detectionConfidence": {"type": "Property", "value": detection_confidence},
                })
            )

        # Retrieve the data model by its ID
        entities = cc.get_all_entities(id_pattern=static_rand_id+"*")
        self.assertEqual(len(entities), len(ids))
        for ret_dm in entities:        
            self.assertIsInstance(ret_dm, DataModels.Face)
            self.assertIn(ret_dm.id, ids)
            ids.remove(ret_dm.id)
            self.assertEqual(e_type, ret_dm.type)
            self.assertEqual(image, ret_dm.image)
            self.assertEqual(BoundingBox(bounding_box["xmin"], bounding_box["ymin"], bounding_box["xmax"], bounding_box["ymax"]),
                            ret_dm.bounding_box)
            self.assertEqual(detection_confidence, ret_dm.detection_confidence)
        self.assertEqual(len(ids), 0)

    def test_post_entity_json(self):
        cc = ContextCli(**config)
        # Create an entity
        e = {
            "id": "urn:ngsi-ld:Test:" + str(uuid.uuid4()),
            "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "type": "Test",
            "test": {"type": "Property", "value": "test_value"}
        }
        # Post the entity
        cc.post_entity_json(e)
        # Get and check the entity from the context broker
        r = requests.get(urljoin(_entities_uri, e["id"]), headers={"Accept": "application/ld+json"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), e)

        # Using a toolbox data model
        e = {
            "id": "urn:ngsi-ld:Face:" + str(uuid.uuid4()),
            "type": "Face",
            "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "dateObserved": {"type": "Property", "value": {"@type": "DateTime", "@value": "2000-01-01T00:00:00Z"}},
            "image": {"type": "Relationship", "object": "urn:ngsi-ld:Image:123",},
            "boundingBox": {"type": "Property", "value": {"xmin": 0.0, "ymin": 0.1, "xmax": 0.2, "ymax": 0.3}},
            "detectionConfidence": {"type": "Property", "value": 0.99},
        }
        cc.post_entity_json(e)
        # Get and check the entity from the context broker
        r = requests.get(urljoin(_entities_uri, e["id"]), headers={"Accept": "application/ld+json"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), e)

    def test_update_entity_json(self):
        cc = ContextCli(**config)
        # Create an entity
        e = {
            "id": "urn:ngsi-ld:Test:" + str(uuid.uuid4()),
            "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "type": "Test",
            "test": {"type": "Property", "value": "test_value"}
        }
        # Post the entity
        r = requests.post(_entities_uri, json=e, headers={"Content-Type": "application/ld+json"})
        # Update the entity
        e["test"]["value"] = "test_value2"
        r = cc.update_entity_json(e)
        self.assertEqual(r, e)
        # Get and check the entity from the context broker
        r = requests.get(urljoin(_entities_uri, e["id"]), headers={"Accept": "application/ld+json"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), e)

        # Test update non existing entity
        e = {
            "id": "urn:ngsi-ld:Test:" + str(uuid.uuid4()),
            "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "type": "Test",
            "test": {"type": "Property", "value": "test_value"}
        }
        # Update the entity
        cc.update_entity_json(e)
        # Get and check the entity from the context broker
        r = requests.get(urljoin(_entities_uri, e["id"]), headers={"Accept": "application/ld+json"})
        self.assertEqual(r.json(), e)

        # Using a toolbox data model
        e = {
            "id": "urn:ngsi-ld:Face:" + str(uuid.uuid4()),
            "type": "Face",
            "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "dateObserved": {"type": "Property", "value": {"@type": "DateTime", "@value": "2000-01-01T00:00:00Z"}},
            "image": {"type": "Relationship", "object": "urn:ngsi-ld:Image:123",},
            "boundingBox": {"type": "Property", "value": {"xmin": 0.0, "ymin": 0.1, "xmax": 0.2, "ymax": 0.3}},
            "detectionConfidence": {"type": "Property", "value": 0.99},
        }
        r = requests.post(_entities_uri, json=e, headers={"Content-Type": "application/ld+json"})
        # Update the entity
        e["detectionConfidence"]["value"] = 0.98
        cc.update_entity_json(e)
        # Get and check the entity from the context broker
        r = requests.get(urljoin(_entities_uri, e["id"]), headers={"Accept": "application/ld+json"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), e)

    def test_post_data_model(self):
        cc = ContextCli(**config)
        # Create a Face data model
        dm = DataModels.Face(
            image="urn:ngsi-ld:Image:001",
            featuresAlgorithm="Algo",
            boundingBox=BoundingBox(0.0,0.1,0.2,0.3)
        )
        # Post the data model with a None id
        entity = cc.post_data_model(dm)
        # Check the returned entity
        self.assertIsInstance(entity, dict)
        self.assertTrue(entity["id"].startswith("urn:ngsi-ld:Face:"))
        self.assertEqual(dm.id, entity["id"])
        self.assertEqual(entity["type"], "Face")
        self.assertEqual(entity["image"]["object"], dm.image)
        self.assertEqual(entity["featuresAlgorithm"]
                         ["value"], dm.features_algorithm)
        self.assertEqual(entity["boundingBox"]["value"], dm.bounding_box.serialize())
        # Get and check the entity from the context broker
        r = requests.get(urljoin(_entities_uri, entity["id"]), headers={"Accept": "application/ld+json"})
        self.assertEqual(r.status_code, 200)
        ret_entity = r.json()
        self.assertEqual(ret_entity["id"], entity["id"])
        self.assertEqual(ret_entity["image"]["object"], dm.image)
        self.assertEqual(ret_entity["featuresAlgorithm"]
                         ["value"], dm.features_algorithm)
        
        # Set an ID and post again
        dm.id = "urn:ngsi-ld:Face:" + str(uuid.uuid4())
        entity = cc.post_data_model(dm)
        self.assertEqual(entity["id"], dm.id)
        # Check that the entity exists
        r = requests.get(urljoin(_entities_uri, dm.id))
        self.assertEqual(r.status_code, 200)
        ret_entity = r.json()
        self.assertEqual(ret_entity["id"], dm.id)
        self.assertEqual(ret_entity["image"]["object"], dm.image)
        self.assertEqual(ret_entity["featuresAlgorithm"]
                         ["value"], dm.features_algorithm)

    def test_update_data_model(self):
        cc = ContextCli(**config)
        # Create a Face data model entity
        dm = DataModels.Face(
            image="urn:ngsi-ld:Image:001",
            featuresAlgorithm="Algo",
            boundingBox=BoundingBox(0.0,0.1,0.2,0.3)
        )
        ret = cc.post_data_model(dm)
        # Update the data model
        dm.features_algorithm = "Algo2"
        cc.update_data_model(dm)
        # Check the returned entity
        ret = cc.get_entity(dm.id)
        self.assertEqual(ret.image, dm.image)
        self.assertEqual(ret.features_algorithm, dm.features_algorithm)
        self.assertEqual(ret.bounding_box, dm.bounding_box)
        self.assertEqual(ret.context, dm.context)

        # Update non existing entity
        dm = DataModels.Face(
            image="urn:ngsi-ld:Image:001",
            featuresAlgorithm="Algo",
            boundingBox=BoundingBox(0.0,0.1,0.2,0.3)
        )
        cc.update_data_model(dm)
        ret = cc.get_entity(dm.id)
        self.assertEqual(ret.image, dm.image)
        self.assertEqual(ret.features_algorithm, dm.features_algorithm)
        self.assertEqual(ret.bounding_box, dm.bounding_box)
        self.assertEqual(ret.context, dm.context)

        # Update non existing entity with create=False
        dm = DataModels.Face(
            image="urn:ngsi-ld:Image:001",
            featuresAlgorithm="Algo",
            boundingBox=BoundingBox(0.0,0.1,0.2,0.3)
        )
        with self.assertRaises(ValueError):
            cc.update_data_model(dm, create=False)

    def test_delete_entity(self):
        cc = ContextCli(**config)
        # Create an entity
        e = {
            "id": "urn:ngsi-ld:Test:" + str(uuid.uuid4()),
            "type": "Test",
            "test": {"type": "Property", "value": "test_value"}
        }
        # Post the entity
        response = requests.post(_entities_uri, json=e)
        self.assertEqual(response.status_code, 201)
        # Retrieve the entity
        response = requests.get(urljoin(_entities_uri, e["id"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), e)
        # Delete the entity
        cc.delete_entity(e["id"])
        # Check that the entity has been deleted
        response = requests.get(urljoin(_entities_uri, e["id"]))
        self.assertEqual(response.status_code, 404)

    def test_get_types(self):
        cc = ContextCli(**config)
        # Create two types
        t1 = "TestType" + str(uuid.uuid4())
        t2 = "TestType" + str(uuid.uuid4())
        # Create one entity for each type
        e1 = {
            "id": "urn:ngsi-ld:Test:" + str(uuid.uuid4()),
            "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "type": t1,
            "test": {"type": "Property", "value": "test_value"}
        }
        e2 = {
            "id": "urn:ngsi-ld:Test:" + str(uuid.uuid4()),
            "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "type": t2,
            "test": {"type": "Property", "value": "test_value"}
        }
        r = requests.post(_entities_uri, json=e1, headers={"Content-Type": "application/ld+json"})
        r = requests.post(_entities_uri, json=e2, headers={"Content-Type": "application/ld+json"})
        # Get the types
        types = cc.get_types()
        self.assertIn(t1, types)
        self.assertIn(t2, types)


if __name__ == "__main__":
    unittest.main()
