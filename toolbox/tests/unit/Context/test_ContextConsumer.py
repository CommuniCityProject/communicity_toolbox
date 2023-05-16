import datetime
import json
import pathlib
import unittest
import uuid

import requests

from toolbox.Context import ContextConsumer
from toolbox.Structures import BoundingBox, Emotion, Gender
from toolbox.utils.config_utils import parse_config

p = pathlib.Path(__file__).parent.resolve()
config = parse_config(p/"config.yaml")
_context_broker_uri = f'http://{config["context_broker"]["host"]}:{config["context_broker"]["port"]}'
_entities_uri = _context_broker_uri + "/ngsi-ld/v1/entities"
_subscriptions_uri = _context_broker_uri + "/ngsi-ld/v1/subscriptions"


class TestContextConsumer(unittest.TestCase):

    # def _compare_subscription(self, sub1, sub2):
    #     comp_keys = ["type", "entities",
    #                  "notification", "watchedAttributes", "q"]
    #     comp_noti_keys = ["format", "endpoint"]
    #     rsub1 = {k: v for k, v in sub1.items() if k in comp_keys}
    #     rsub2 = {k: v for k, v in sub2.items() if k in comp_keys}
    #     rsub1["notification"] = {
    #         k: v for k, v in rsub1["notification"].items() if k in comp_noti_keys}
    #     rsub2["notification"] = {
    #         k: v for k, v in rsub2["notification"].items() if k in comp_noti_keys}
    #     self.assertEqual(rsub1, rsub2)

    # def _get_subscription(self, sub_id):
    #     r = requests.get(f"{_subscriptions_uri}/{sub_id}")
    #     return r.ok, r.status_code

    def test_init(self):
        cc = ContextConsumer(config)
        self.assertEqual(cc.notification_uri, config["context_broker"]["notification_uri"])
        self.assertTrue(cc.subscription_name)

    def test_build_subscription(self):
        cc = ContextConsumer(config)
        
        sub = cc.build_subscription("Ty")
        self.assertEqual(sub["type"], "Subscription")
        self.assertEqual(sub["entities"], [{"type": "Ty"}])
        self.assertEqual(sub["notification"]["format"], "normalized")
        self.assertEqual(sub["notification"]["endpoint"]["uri"], config["context_broker"]["notification_uri"])
        self.assertEqual(sub["notification"]["endpoint"]["accept"], "application/json")
        self.assertEqual(sub["name"], cc.subscription_name)
    
        sub = cc.build_subscription(
            entity_type="Ty",
            uri="http://1.2.3.4:5678",
            subscription_id="1234",
            name="a_name",
            description="a_description",
            entity_id="an_entity_id",
            entity_id_pattern="an_entity_id_pattern",
            watched_attributes=["a1", "a2"],
            query="a1==true",
            notification_attributes=["b1", "b2"],
            notification_format="keyValues",
            notification_accept="application/json",
            expires="2021-01-01T00:00:00Z",
            throttling=5,
        )
        self.assertEqual(sub["type"], "Subscription")
        self.assertEqual(sub["entities"], [{"type": "Ty", "id": "an_entity_id", "idPattern": "an_entity_id_pattern"}])
        self.assertEqual(sub["notification"]["endpoint"]["uri"], "http://1.2.3.4:5678")
        self.assertEqual(sub["id"], "1234")
        self.assertEqual(sub["name"], "a_name")
        self.assertEqual(sub["description"], "a_description")
        self.assertEqual(sub["entities"][0]["id"], "an_entity_id")
        self.assertEqual(sub["entities"][0]["idPattern"], "an_entity_id_pattern")
        self.assertEqual(sub["watchedAttributes"], ["a1", "a2"])
        self.assertEqual(sub["q"], "a1==true")
        self.assertEqual(sub["notification"]["attributes"], ["b1", "b2"])
        self.assertEqual(sub["notification"]["format"], "keyValues")
        self.assertEqual(sub["notification"]["endpoint"]["accept"], "application/json")
        self.assertEqual(sub["expires"], "2021-01-01T00:00:00Z")
        self.assertEqual(sub["throttling"], 5)

    def test_subscribe(self):
        cc = ContextConsumer(config)

        # Test subscription creation
        id_0 = cc.subscribe(entity_type="Ty")
        self.assertIsNotNone(id_0)
        self.assertEqual(cc.subscription_ids[0], id_0)

        # Test subscription post
        sub = cc.build_subscription(
            entity_type="Ty",
            uri="http://1.2.3.4:5678",
            name="a_name",
            description="a_description",
            entity_id="urn:ngsi-ld:Ty:123",
            watched_attributes=["a1", "a2"],
            query="a1==true",
            notification_attributes=["b1", "b2"],
            notification_format="keyValues",
            notification_accept="application/ld+json",
            expires="2021-01-01T00:00:00.000Z",
            throttling=5,
        )
        id_1 = cc.subscribe(sub)
        self.assertIsNotNone(id_1)
        self.assertEqual(cc.subscription_ids[1], id_1)

        id_2 = cc.subscribe(
            entity_type="Ty",
            uri="http://1.2.3.4:5678",
            name="a_name",
            description="a_description",
            entity_id="urn:ngsi-ld:Ty:123",
            watched_attributes=["a1", "a2"],
            query="a1==true",
            notification_attributes=["b1", "b2"],
            notification_format="keyValues",
            notification_accept="application/ld+json",
            expires="2021-01-01T00:00:00.000Z",
            throttling=5
        )
        self.assertIsNotNone(id_2)
        self.assertEqual(cc.subscription_ids[2], id_2)
        
        self.assertNotEqual(id_0, id_1)
        
        # Get the subscriptions
        r = requests.get(f"{_subscriptions_uri}/{id_0}")
        self.assertTrue(r.ok)
        ret_sub = r.json()
        self.assertEqual(ret_sub["id"], id_0)
        self.assertEqual(ret_sub["type"], "Subscription")
        self.assertEqual(ret_sub["subscriptionName"], cc.subscription_name)
        self.assertEqual(ret_sub["entities"], [{"type": "Ty"}])
        self.assertEqual(ret_sub["notification"]["format"], "normalized")
        self.assertEqual(ret_sub["notification"]["endpoint"]["uri"], config["context_broker"]["notification_uri"])
        self.assertEqual(ret_sub["notification"]["endpoint"]["accept"], "application/json")

        r = requests.get(f"{_subscriptions_uri}/{id_1}")
        self.assertTrue(r.ok)
        ret_sub = r.json()
        self.assertEqual(ret_sub["id"], id_1)
        self.assertEqual(ret_sub["type"], "Subscription")
        self.assertEqual(ret_sub["subscriptionName"], "a_name")
        self.assertEqual(ret_sub["description"], "a_description")
        self.assertEqual(ret_sub["entities"], [{"type": "Ty", "id": "urn:ngsi-ld:Ty:123"}])
        self.assertEqual(ret_sub["watchedAttributes"], ["a1", "a2"])
        self.assertEqual(ret_sub["q"], "a1==true")
        self.assertEqual(ret_sub["notification"]["attributes"], ["b1", "b2"])
        self.assertEqual(ret_sub["notification"]["format"], "keyValues")
        self.assertEqual(ret_sub["notification"]["endpoint"]["uri"], "http://1.2.3.4:5678")
        self.assertEqual(ret_sub["notification"]["endpoint"]["accept"], "application/ld+json")
        self.assertEqual(ret_sub["expiresAt"], "2021-01-01T00:00:00.000Z")
        self.assertEqual(ret_sub["throttling"], 5)

    def test_get_subscription(self):
        cc = ContextConsumer(config)
        s_id = cc.subscribe(
            entity_type="Ty",
            uri="http://1.2.3.4:5678",
            name="a_name",
            description="a_description",
            entity_id="urn:ngsi-ld:Ty:123",
            watched_attributes=["a1", "a2"],
            query="a1==true",
            notification_attributes=["b1", "b2"],
            notification_format="keyValues",
            notification_accept="application/ld+json",
            expires="2021-01-01T00:00:00.000Z",
            throttling=5
        )
        self.assertIsNotNone(s_id)
        sub = cc.get_subscription(s_id)
        self.assertEqual(sub["id"], s_id)
        self.assertEqual(sub["type"], "Subscription")
        self.assertEqual(sub["subscriptionName"], "a_name")
        self.assertEqual(sub["description"], "a_description")
        self.assertEqual(sub["entities"], [{"type": "Ty", "id": "urn:ngsi-ld:Ty:123"}])
        self.assertEqual(sub["watchedAttributes"], ["a1", "a2"])
        self.assertEqual(sub["q"], "a1==true")
        self.assertEqual(sub["notification"]["attributes"], ["b1", "b2"])
        self.assertEqual(sub["notification"]["format"], "keyValues")
        self.assertEqual(sub["notification"]["endpoint"]["uri"], "http://1.2.3.4:5678")
        self.assertEqual(sub["notification"]["endpoint"]["accept"], "application/ld+json")
        self.assertEqual(sub["expiresAt"], "2021-01-01T00:00:00.000Z")
        self.assertEqual(sub["throttling"], 5)

        sub = cc.get_subscription("none")
        self.assertIsNone(sub)

    def test_get_subscriptions(self):
        cc = ContextConsumer(config)
        for _ in range(6):
            cc.subscribe(entity_type="Ty")
        subs_0 = cc.get_subscriptions(3,0)
        subs_1 = cc.get_subscriptions(3,1)
        self.assertEqual(len(subs_0), 3)
        self.assertEqual(len(subs_1), 3)
        self.assertEqual(subs_0[1], subs_1[0])
        self.assertEqual(subs_0[2], subs_1[1])
        self.assertNotEqual(subs_0[0], subs_1[2])

    def test_iterate_subscriptions(self):
        cc = ContextConsumer(config)
        for _ in range(6):
            cc.subscribe(entity_type="Ty")
        it = cc.iterate_subscriptions(3)
        subs_0 = next(it)
        subs_1 = next(it)
        self.assertEqual(len(subs_0), 3)
        self.assertEqual(len(subs_1), 3)
        set_0 = set([s["id"] for s in subs_0])
        set_1 = set([s["id"] for s in subs_1])
        self.assertEqual(len(set_0), 3)
        self.assertEqual(len(set_1), 3)
        self.assertEqual(len(set_0.intersection(set_1)), 0)

    def test_get_all_subscriptions(self):
        cc = ContextConsumer(config)
        pre_subs = cc.get_all_subscriptions()
        for _ in range(6):
            s_id = cc.subscribe(entity_type="Ty")
        post_subs = cc.get_all_subscriptions()
        self.assertEqual(len(pre_subs) + 6, len(post_subs))
        self.assertIn(s_id, set([s["id"] for s in post_subs]))

    def test_subscription_equals(self):
        cc = ContextConsumer(config)
        params = {
            "entity_type": "Ty",
            "uri": "http://1.2.3.4:5678",
            "subscription_id": "1234",
            "name": "a_name",
            "description": "a_description",
            "entity_id": "an_entity_id",
            "entity_id_pattern": "an_entity_id_pattern",
            "watched_attributes": ["a1", "a2"],
            "query": "a1==true",
            "notification_attributes": ["b1", "b2"],
            "notification_format": "keyValues",
            "notification_accept": "application/json",
            "expires": "2021-01-01T00:00:00Z",
            "throttling": 5,
        }
        sub_1 = cc.build_subscription(**params)
        params_mod = params.copy()
        self.assertTrue(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        params_mod["entity_type"] = "TT"
        self.assertFalse(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        params_mod["uri"] = "http://1.2.3.4:5778"
        self.assertFalse(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        params_mod["subscription_id"] = "1235"
        self.assertTrue(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        params_mod["name"] = "q_name"
        self.assertTrue(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        params_mod["description"] = "q_description"
        self.assertTrue(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        params_mod["entity_id"] = "an_entity_ii"
        self.assertFalse(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        params_mod["entity_id_pattern"] = "aa_entity_id_pattern"
        self.assertFalse(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        params_mod["watched_attributes"] = ["a2", "a2"],
        self.assertFalse(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        params_mod["query"] = "a1==false",
        self.assertFalse(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        params_mod["notification_attributes"] = ["b1", "b3"],
        self.assertFalse(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        params_mod["notification_format"] = "normalized",
        self.assertFalse(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        params_mod["notification_accept"] = "application/ld+json",
        self.assertFalse(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        params_mod["expires"] = "2021-01-02T00:00:00Z",
        self.assertFalse(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )
        params_mod = params.copy()
        # params_mod["throttling"] = 5,
        self.assertTrue(
            cc.subscription_equals(sub_1, cc.build_subscription(**params_mod))
        )


    def test_subscription_conflicts(self):
        cc = ContextConsumer(config)
        t = str(uuid.uuid4())
        s_id = cc.subscribe(t, ["a1"], "a1==true")
        self.assertEqual(len(cc.subscription_conflicts(
            str(uuid.uuid4()), ["a1"], "a1==true")), 0)
        self.assertEqual(len(cc.subscription_conflicts(
            t, [uuid.uuid4()], "a1==true")), 0)
        self.assertEqual(len(cc.subscription_conflicts(
            t, ["a1"], f"{uuid.uuid4()}==true")), 0)
        self.assertEqual(len(cc.subscription_conflicts(
            t, ["a1"], "a1==false")), 0)
        self.assertGreater(
            len(cc.subscription_conflicts(t, ["a1"], "a1==true")), 0)

    # def test_unsubscribe(self):
    #     cc = ContextConsumer(config)

    #     s_id0 = cc.subscribe("T0")
    #     s_id1 = cc.subscribe("T1")
    #     s_id2 = cc.subscribe("T2")
    #     s_id3 = cc.subscribe("T3")

    #     self.assertEqual(len(cc.subscription_ids), 4)
    #     self.assertTrue(cc.unsubscribe(s_id0))
    #     self.assertEqual(len(cc.subscription_ids), 3)
    #     self.assertFalse(cc.unsubscribe(s_id0))
    #     self.assertEqual(len(cc.subscription_ids), 3)
    #     self.assertFalse(cc.unsubscribe("0"))
    #     self.assertEqual(len(cc.subscription_ids), 3)

    def test_parse_entity(self):
        cc = ContextConsumer(config)
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
        ret_dm = cc.parse_entity(e_id)
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
        with self.assertRaises(ValueError):
            cc.parse_entity("0")

    def test_parse_dict(self):
        cc = ContextConsumer(config)
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
        entity = {
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
        }
        dm = cc.parse_dict(entity)
        self.assertEqual(e_id, dm.id)
        self.assertEqual(e_type, dm.type)
        self.assertEqual(datetime.datetime.fromisoformat(
            date_observed[:-1]), dm.dateObserved)
        self.assertEqual(image, dm.image)
        self.assertEqual(BoundingBox(bounding_box["xmin"], bounding_box["ymin"], bounding_box["xmax"], bounding_box["ymax"]),
                         dm.bounding_box)
        self.assertEqual(detection_confidence, dm.detection_confidence)
        self.assertEqual(age, dm.age)
        self.assertEqual(Gender[gender], dm.gender)
        self.assertEqual(gender_confidence, dm.gender_confidence)
        self.assertEqual(Emotion[emotion], dm.emotion)
        self.assertEqual(emotion_confidence, dm.emotion_confidence)
        self.assertEqual(features, dm.features)
        self.assertEqual(features_algorithm, dm.features_algorithm)
        self.assertEqual(recognition_domain, dm.recognition_domain)
        self.assertEqual(recognized, dm.recognized)
        self.assertEqual(recognized_distance, dm.recognized_distance)
        self.assertEqual(recognized_person, dm.recognized_person)


if __name__ == "__main__":
    unittest.main()
