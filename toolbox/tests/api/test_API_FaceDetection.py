import unittest
import requests
import datetime

from toolbox.Structures import BoundingBox
from toolbox import DataModels
from toolbox.Context import ContextCli

import config

API_URL = f"http://{config.HOST}:{config.FACE_RECOGNITION_API_PORT}"
BROKER_URL = f"http://{config.HOST}:{config.CONTEXT_BROKER_PORT}/ngsi-ld/v1/entities/"


class test_API_FaceRecognition(unittest.TestCase):

    def test_root(self):
        """Test get /
        """
        r = requests.get(API_URL)
        self.assertTrue(r.ok, r.text)

    def test_docs(self):
        """Test get /docs
        """
        r = requests.get(API_URL + "/docs")
        self.assertTrue(r.ok, r.text)

    def test_redoc(self):
        """Test get /redoc
        """
        r = requests.get(API_URL + "/redoc")
        self.assertTrue(r.ok, r.text)

    def _test_entity_fields(self, entity: dict, images_id: str = None,
                            is_json_ld: bool = False):
        if is_json_ld:
            def get_value(d, x): return d[x]["value"]
        else:
            def get_value(d, x): return d[x]

        # Type
        self.assertEqual(entity["type"], "Face")

        # Id
        self.assertIn("id", entity)

        # dateObserved
        if is_json_ld:
            date_str = entity["dateObserved"]["value"]["@value"]
        else:
            date_str = entity["dateObserved"]
        date_str = date_str.replace("Z", "")
        date_str.rsplit(".", 1)[0]
        date = datetime.datetime.fromisoformat(date_str)
        self.assertEqual(date.isoformat(), date_str)

        # image
        self.assertIn("image", entity)
        if images_id is not None:
            if is_json_ld:
                image_str = entity["image"]["object"]
            else:
                image_str = entity["image"]
            self.assertEqual(image_str, images_id)

        # BoundingBox
        bb_dict = get_value(entity, "boundingBox")
        bb = BoundingBox.deserialize(bb_dict)
        self.assertEqual(bb.serialize(), bb_dict)

        # detectionConfidence
        self.assertGreater(get_value(entity, "detectionConfidence"), 0)

        # features
        self.assertGreater(len(get_value(entity, "features")), 0)

        # featuresAlgorithm
        self.assertIn("featuresAlgorithm", entity)

        # recognitionDomain
        self.assertIn("recognitionDomain", entity)

        # recognizedPerson
        self.assertIn("recognizedPerson", entity)

        # recognized
        self.assertTrue(get_value(entity, "recognized"))

        # recognizedDistance
        self.assertGreater(get_value(entity, "recognizedDistance"), 0)

    def test_predict_image(self):
        """Test get /predict with an image entity
        """
        # Get image id
        with open(config.IMG_FACES_ID_PATH, "r") as f:
            img_id = f.read()

        # Predict image
        r = requests.post(API_URL + "/predict", json={"entity_id": img_id})
        self.assertTrue(r.ok, r.text)
        self.assertEqual(r.headers["content-type"], "application/json")
        entities = r.json()
        self.assertEqual(len(entities), 4)

        for ent in entities:
            # Check entities
            self._test_entity_fields(ent, img_id)
            # Check exists in context broker
            r = requests.get(BROKER_URL + ent["id"])
            self.assertTrue(r.ok, r.text)
            ret_ent = r.json()
            # Check context broker entity
            self._test_entity_fields(ret_ent, img_id, True)

        # Predict with accept: json-ld
        r = requests.post(API_URL + "/predict", json={"entity_id": img_id},
                          headers={"accept": "application/ld+json"})
        self.assertTrue(r.ok, r.text)
        self.assertEqual(r.headers["content-type"], "application/ld+json")
        entities = r.json()
        self.assertEqual(len(entities), 4)

        for ent in entities:
            # Check entities
            self._test_entity_fields(ent, img_id, True)
            # Check exists in context broker
            r = requests.get(BROKER_URL + ent["id"])
            self.assertTrue(r.ok, r.text)
            ret_ent = r.json()
            # Check context broker entity
            self._test_entity_fields(ret_ent, img_id, True)

        # Predict without posting to context broker
        r = requests.post(
            API_URL + "/predict",
            json={"entity_id": img_id, "post_to_broker": False}
        )
        self.assertTrue(r.ok, r.text)
        self.assertEqual(r.headers["content-type"], "application/json")
        entities = r.json()
        self.assertEqual(len(entities), 4)

        for ent in entities:
            # Check entities
            self._test_entity_fields(ent, img_id)
            # Check exists in context broker
            self.assertIsNone(ent["id"])

    def test_predict_face(self):
        """Test get /predict with a face entity
        """
        # Create a context producer
        cc = ContextCli(
            host=config.HOST,
            port=config.CONTEXT_BROKER_PORT,
        )
        
        # Get image id
        with open(config.IMG_FACES_ID_PATH, "r") as f:
            img_id = f.read()

        face_params = {
            "age": 20,
            "boundingBox": BoundingBox(0.58, 0.6, 0.806, 0.835),
            "detectionConfidence": 0.999,
            "image": img_id
        }
        face_dm = DataModels.Face(**face_params)
        cc.post_data_model(face_dm)
        self.assertIsNotNone(face_dm.id)

        # Predict Face
        r = requests.post(API_URL + "/predict", json={"entity_id": face_dm.id})
        self.assertTrue(r.ok, r.text)
        entities = r.json()
        self.assertEqual(len(entities), 1)
        entity = entities[0]

        # Check entities
        self._test_entity_fields(entity)
        self.assertEqual(entity["age"], face_params["age"])
        self.assertEqual(entity["detectionConfidence"],
                         face_params["detectionConfidence"])
        self.assertEqual(entity["image"], face_params["image"])
        self.assertEqual(entity["boundingBox"],
                         face_params["boundingBox"].serialize())

        # Check exists in context broker
        r = requests.get(BROKER_URL + entity["id"])
        self.assertTrue(r.ok, r.text)
        ret_ent = r.json()
        # Check context broker entity
        self._test_entity_fields(ret_ent, is_json_ld=True)
        self.assertEqual(ret_ent["age"]["value"], face_params["age"])
        self.assertEqual(ret_ent["detectionConfidence"]["value"],
                         face_params["detectionConfidence"])
        self.assertEqual(ret_ent["image"]["object"], face_params["image"])
        self.assertEqual(ret_ent["boundingBox"]["value"],
                         face_params["boundingBox"].serialize())

if __name__ == "__main__":
    unittest.main()
