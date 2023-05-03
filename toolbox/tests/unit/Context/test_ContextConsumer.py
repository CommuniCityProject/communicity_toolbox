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

    def _compare_subscription(self, sub1, sub2):
        comp_keys = ["type", "entities",
                     "notification", "watchedAttributes", "q"]
        comp_noti_keys = ["format", "endpoint"]
        rsub1 = {k: v for k, v in sub1.items() if k in comp_keys}
        rsub2 = {k: v for k, v in sub2.items() if k in comp_keys}
        rsub1["notification"] = {
            k: v for k, v in rsub1["notification"].items() if k in comp_noti_keys}
        rsub2["notification"] = {
            k: v for k, v in rsub2["notification"].items() if k in comp_noti_keys}
        self.assertEqual(rsub1, rsub2)

    def _get_subscription(self, sub_id):
        r = requests.get(f"{_subscriptions_uri}/{sub_id}")
        return r.ok, r.status_code

    def test_init(self):
        cc = ContextConsumer(config)

    def test_subscribe(self):
        cc = ContextConsumer(config)

        id_0 = cc.subscribe("Ty")
        self.assertIsNotNone(id_0)
        self.assertEqual(cc.subscription_ids[0], id_0)

        id_1 = cc.subscribe("Ty")
        self.assertIsNotNone(id_1)
        self.assertEqual(cc.subscription_ids[1], id_1)
        self.assertNotEqual(id_0, id_1)

        s_id = cc.subscribe("Ty", ["a1"], "a1==true")
        r = requests.get(f"{_subscriptions_uri}/{s_id}")
        self.assertTrue(r.ok)
        self._compare_subscription(
            r.json(),
            {
                "type": "Subscription",
                "entities": [{"type": "Ty"}],
                "watchedAttributes": ["a1"],
                "q": "a1==true",
                "notification": {
                    "format": "normalized",
                    "endpoint": {
                        "uri": config["context_broker"]["notification_uri"],
                        "accept": "application/json"
                    }
                }
            }
        )

    def test_get_subscriptions(self):
        cc = ContextConsumer(config)
        s_id = cc.subscribe("Ty", ["a1"], "a1==true")
        subs = cc.get_subscriptions()
        self.assertGreater(len(subs), 0)
        sub = [s for s in subs if s["id"] == s_id]
        self.assertEqual(len(sub), 1)
        sub = sub[0]
        self._compare_subscription(
            sub,
            {
                "type": "Subscription",
                "entities": [{"type": "Ty"}],
                "watchedAttributes": ["a1"],
                "q": "a1==true",
                "notification": {
                    "format": "normalized",
                    "endpoint": {
                        "uri": config["context_broker"]["notification_uri"],
                        "accept": "application/json"
                    }
                }
            }
        )

    def test_subscription_conflicts(self):
        cc = ContextConsumer(config)
        t = str(uuid.uuid4())
        s_id = cc.subscribe(t, ["a1"], "a1==false")
        self.assertEqual(len(cc.subscription_conflicts(
            str(uuid.uuid4()), ["a1"], "a1==false")), 0)
        self.assertEqual(len(cc.subscription_conflicts(
            t, [uuid.uuid4()], "a1==false")), 0)
        self.assertEqual(len(cc.subscription_conflicts(
            t, ["a1"], f"{uuid.uuid4()}==false")), 0)
        self.assertEqual(len(cc.subscription_conflicts(
            t, ["a1"], "a1==true")), 0)
        self.assertGreater(
            len(cc.subscription_conflicts(t, ["a1"], "a1==false")), 0)

    def test_unsubscribe(self):
        cc = ContextConsumer(config)

        s_id0 = cc.subscribe("T0")
        s_id1 = cc.subscribe("T1")
        s_id2 = cc.subscribe("T2")
        s_id3 = cc.subscribe("T3")

        self.assertEqual(len(cc.subscription_ids), 4)
        self.assertTrue(cc.unsubscribe(s_id0))
        self.assertEqual(len(cc.subscription_ids), 3)
        self.assertFalse(cc.unsubscribe(s_id0))
        self.assertEqual(len(cc.subscription_ids), 3)
        self.assertFalse(cc.unsubscribe("0"))
        self.assertEqual(len(cc.subscription_ids), 3)

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
