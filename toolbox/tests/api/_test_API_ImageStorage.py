import requests
import unittest
import hashlib
import cv2
import tempfile
from pathlib import Path

import config

API_URL = f"http://{config.HOST}:{config.IMAGE_STORAGE_API_PORT}/"
BROKER_URL = f"http://{config.HOST}:{config.CONTEXT_BROKER_PORT}/ngsi-ld/v1/entities/"


class TestImageStorage(unittest.TestCase):

    def _test_get_image(self, url: str, path: str):
        """Test that the image at the given url is the same as the one at
        the given path.
        """
        r = requests.get(url)
        self.assertTrue(r.ok, r.text)
        with open(path, "rb") as f:
            hash_local = hashlib.sha256(f.read()).hexdigest()
        hash_api = hashlib.sha256(r.content).hexdigest()
        self.assertEqual(hash_local, hash_api)

    def test_docs(self):
        """Test /docs
        """
        r = requests.get(API_URL + "docs")
        self.assertTrue(r.ok, r.text)

    def test_redoc(self):
        """Test /redoc
        """
        r = requests.get(API_URL + "redoc")
        self.assertTrue(r.ok, r.text)

    def test_post_get(self):
        """Test post an image file and get it back.
        """
        # Get image width and height
        img = cv2.imread(config.IMG_FACES_PATH)
        img_h, img_w = img.shape[:2]

        # Post image
        with open(config.IMG_FACES_PATH, "rb") as img_file:
            files = {"file": ("test.png", img_file, "image/png")}
            data = {
                "source": "test_source",
                "purpose": "test_purpose"
            }
            headers = {"accept": "application/json"}
            r = requests.post(API_URL, headers=headers, data=data, files=files)
        self.assertTrue(r.ok, r.text)
        img_id = r.json()
        with open(config.IMG_FACES_ID_PATH, "w") as f:
            f.write(img_id)
        self.assertIsInstance(img_id, str)
        self.assertTrue(img_id.startswith("urn:ngsi-ld:Image:"), img_id)

        # Get entity from context broker
        r = requests.get(BROKER_URL + img_id)
        self.assertTrue(r.ok, r.text)
        entity = r.json()
        self.assertEqual(entity["source"]["value"], data["source"])
        self.assertEqual(entity["purpose"]["value"], data["purpose"])
        self.assertEqual(entity["width"]["value"], img_w)
        self.assertEqual(entity["height"]["value"], img_h)
        self.assertEqual(entity["type"], "Image")

        # Get image from API
        self._test_get_image(API_URL + img_id, config.IMG_FACES_PATH)

        # Get image by url
        self._test_get_image(entity["url"]["value"], config.IMG_FACES_PATH)

    def test_post_errors(self):
        """Test generated errors when uploading non allowed files.
        """
        # Create a non image file
        with tempfile.TemporaryFile() as fp:
            fp.write(b"not an image")

            # Post file with fake mime
            files = {"file": ("test.png", fp, "image/png")}
            data = {
                "source": "test_source",
                "purpose": "test_purpose"
            }
            headers = {"accept": "application/json"}
            r = requests.post(API_URL, headers=headers, data=data, files=files)
            self.assertEqual(r.status_code, 422)

            # Post non image file
            files = {"file": ("test.png", fp, "text/plain")}
            data = {
                "source": "test_source",
                "purpose": "test_purpose"
            }
            headers = {"accept": "application/json"}
            r = requests.post(API_URL, headers=headers, data=data, files=files)
            self.assertEqual(r.status_code, 415)

            # Post without files
            data = {
                "source": "test_source",
                "purpose": "test_purpose"
            }
            headers = {"accept": "application/json"}
            r = requests.post(API_URL, headers=headers, data=data)
            self.assertEqual(r.status_code, 422)

        # Post a large file
        with tempfile.TemporaryFile() as fp:
            # Write n bytes to file
            for i in range(int(config.LARGE_FILE_BSIZE)):
                fp.write(b"h")
            # Post the file
            files = {"file": ("test.png", fp, "image/png")}
            data = {
                "source": "test_source",
                "purpose": "test_purpose"
            }
            fp.seek(0)
            headers = {"accept": "application/json"}
            r = requests.post(API_URL, headers=headers, data=data, files=files)
            self.assertEqual(r.status_code, 413)


if __name__ == "__main__":
    unittest.main()
