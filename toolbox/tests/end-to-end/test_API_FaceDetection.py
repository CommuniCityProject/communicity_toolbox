import unittest
import requests

import config

API_URL = f"http://{config.HOST}:{config.FACE_DETECTION_API_PORT}"
BROKER_URL = f"http://{config.HOST}:{config.CONTEXT_BROKER_PORT}/ngsi-ld/v1/entities/"


class test_API_FaceDetection(unittest.TestCase):



    def test_root(self):
        r = requests.get(API_URL)
        self.assertTrue(r.ok, r.text)

    def test_docs(self):
        r = requests.get(API_URL + "/docs")
        self.assertTrue(r.ok, r.text)
    
    def test_redoc(self):
        r = requests.get(API_URL + "/redoc")
        self.assertTrue(r.ok, r.text)
    
    def test_redoc(self):
        r = requests.get(API_URL + "/redoc")
        self.assertTrue(r.ok, r.text)

    def test_predict_image(self):
        # Get image id
        with open(config.IMG_FACES_ID_PATH, "r") as f:
            img_id = f.read()
        # Post image
        r = requests.post(API_URL + "/predict", json={"entity_id": img_id})
        self.assertTrue(r.ok, r.text)
        entities = r.json()
        self.assertEqual(len(entities), 4)
        for ent in entities:
            print(ent)
            self.assertEqual(ent["type"], "Face")
            self.assertIn("id", ent)
            self.assertEqual(ent["image"], img_id)
            self.assertIn("boundingBox", ent)
            self.assertGreater(ent["detectionConfidence"], 0)
            self.assertGreater(len(ent["features"]), 0)
            self.assertTrue(len(ent["recognized"]))
        # Check is in context broker
        r = requests.get(BROKER_URL + ent["id"])
        self.assertTrue(r.ok, r.text)
        ret_ent = r.json()
        self.assertEqual(ret_ent["type"], "Face")
        self.assertEqual(ret_ent["image"]["value"], ent["image"])
        self.assertEqual(ret_ent["boundingBox"]["value"], ent["boundingBox"])
        self.assertEqual(ret_ent["detectionConfidence"]["value"], ent["detectionConfidence"])
        self.assertEqual(ret_ent["features"]["value"], ent["features"])
        self.assertEqual(ret_ent["recognized"]["value"], ent["recognized"])

        # Get json-ld




if __name__ == "__main__":
    unittest.main()