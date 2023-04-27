import pathlib
import unittest
import uuid

import ngsildclient
import requests

from toolbox import DataModels
from toolbox.Context import ContextProducer
from toolbox.Structures import BoundingBox, Emotion, Gender
from toolbox.utils.config_utils import parse_config

p = pathlib.Path(__file__).parent.resolve()
config = parse_config(p/"config.yaml")
_context_broker_uri = f'http://{config["context_broker"]["host"]}:{config["context_broker"]["port"]}'
_entities_uri = _context_broker_uri + "/ngsi-ld/v1/entities"


class TestContextProducer(unittest.TestCase):

    def _get_entity(self, entity_id):
        r = requests.get(f"{_entities_uri}/{entity_id}")
        return r.status_code, r.json()

    def test_init(self):
        cp = ContextProducer(config)

    def test_post_entity(self):
        cp = ContextProducer(config)
        # Create a Face data model
        dm = DataModels.Face(
            image="urn:ngsi-ld:Image:001",
            featuresAlgorithm="Algo"
        )
        # Post the data model with a None id
        entity = cp.post_entity(dm)
        # Check the returned entity
        self.assertIsInstance(entity, dict)
        self.assertIsInstance(entity["id"], str)
        self.assertNotEqual(entity["id"], "")
        self.assertEqual(dm.id, entity["id"])
        self.assertEqual(entity["type"], "Face")
        self.assertIn("image", entity)
        self.assertEqual(entity["image"]["object"], dm.image)
        self.assertEqual(entity["featuresAlgorithm"]
                         ["value"], dm.features_algorithm)
        # Get and check the entity from the context broker
        code, ret_entity = self._get_entity(entity["id"])
        self.assertEqual(code, 200)
        self.assertEqual(ret_entity["id"], entity["id"])
        self.assertEqual(ret_entity["image"]["object"], dm.image)
        self.assertEqual(ret_entity["featuresAlgorithm"]
                         ["value"], dm.features_algorithm)
        # Set an id and post again
        _id = "urn:ngsi-ld:Face:" + str(uuid.uuid4())
        dm.id = _id
        entity = cp.post_entity(dm)
        self.assertEqual(entity["id"], _id)
        self.assertEqual(dm.id, _id)
        # Check that the entity exists
        code, ret_entity = self._get_entity(entity["id"])
        self.assertIsNotNone(ret_entity)

    def test_to_json(self):
        cp = ContextProducer(config)
        # Create a Face data model
        args = {
            "id": "urn:ngsi-ld:Face:123",
            "image": "urn:ngsi-ld:Image:123",
            "bounding_box": BoundingBox(0.1, 0.2, 0.3, 0.4),
            "detection_confidence": 0.99,
            "age": 30.5,
            "gender": Gender.FEMALE,
            "gender_confidence": 0.88,
            "emotion": Emotion.HAPPINESS,
            "emotion_confidence": 0.77,
            "features": [1.1, 2.2, 3.3],
            "features_algorithm": "algorithm",
            "recognition_domain": "domain",
            "recognized": False,
            "recognized_distance": 2.2,
            "recognized_person": "person"
        }
        # Create a face data model with the above values
        dm = DataModels.Face(**args)
        json_data = cp.to_json(dm)
        # Check the json
        self.assertEqual(json_data["id"], args["id"])
        self.assertEqual(json_data["image"]["object"], args["image"])
        self.assertEqual(
            BoundingBox.deserialize(json_data["boundingBox"]["value"]),
            args["bounding_box"]
        )
        self.assertEqual(
            json_data["detectionConfidence"]["value"],
            args["detection_confidence"]
        )
        self.assertEqual(json_data["age"]["value"], args["age"])
        self.assertEqual(Gender[json_data["gender"]["value"]], args["gender"])
        self.assertEqual(json_data["genderConfidence"]
                         ["value"], args["gender_confidence"])
        self.assertEqual(
            Emotion[json_data["emotion"]["value"]],
            args["emotion"]
        )
        self.assertEqual(
            json_data["emotionConfidence"]["value"],
            args["emotion_confidence"]
        )
        self.assertEqual(json_data["features"]["value"], args["features"])
        self.assertEqual(
            json_data["featuresAlgorithm"]["value"],
            args["features_algorithm"]
        )
        self.assertEqual(
            json_data["recognitionDomain"]["value"],
            args["recognition_domain"]
        )
        self.assertEqual(json_data["recognized"]["value"], args["recognized"])
        self.assertEqual(
            json_data["recognizedDistance"]["value"],
            args["recognized_distance"]
        )
        self.assertEqual(json_data["recognizedPerson"]
                         ["value"], args["recognized_person"])

    def test_update_entity(self):
        cp = ContextProducer(config)
        # Create a Face data model
        dm = DataModels.Face(
            image="urn:ngsi-ld:Image:001",
            featuresAlgorithm="Algo"
        )
        # Post the data model
        entity = cp.post_entity(dm)
        # Get the entity from the context broker
        code, ret_entity = self._get_entity(entity["id"])
        self.assertEqual(code, 200)
        # Check age is not present
        self.assertNotIn("age", ret_entity)
        # Update the entity age
        self.assertIsNotNone(dm.id)
        dm.age = 30.5
        cp.update_entity(dm)
        # Get the entity from the context broker
        code, ret_entity = self._get_entity(entity["id"])
        self.assertEqual(code, 200)
        # Check age is updated
        self.assertEqual(ret_entity["age"]["value"], dm.age)

        # Check raises when id is None
        dm.id = None
        with self.assertRaises(ValueError):
            cp.update_entity(dm)

        # Check raises when id is not present in the context broker
        dm.id = "urn:ngsi-ld:Face:123"
        with self.assertRaises(ngsildclient.api.exceptions.NgsiResourceNotFoundError):
            cp.update_entity(dm)

    def test_delete_entity(self):
        cp = ContextProducer(config)
        # Create a Face data model
        dm = DataModels.Face(
            image="urn:ngsi-ld:Image:001",
            featuresAlgorithm="Algo"
        )
        # Post the data model
        entity = cp.post_entity(dm)
        # Check the entity exists
        code, ret_entity = self._get_entity(entity["id"])
        self.assertEqual(code, 200)
        self.assertIsNotNone(ret_entity)
        # Delete the entity
        success = cp.delete_entity(dm.id)
        self.assertTrue(success)
        success = cp.delete_entity(dm.id)
        self.assertFalse(success)
        # Check the entity does not exist
        code, ret_entity = self._get_entity(entity["id"])
        self.assertEqual(code, 404)


if __name__ == "__main__":
    unittest.main()
