import pytest
import requests
import hashlib
import cv2
import tempfile

import config

API_URL = f"http://{config.HOST}:{config.IMAGE_STORAGE_API_PORT}/"
BROKER_URL = f"http://{config.HOST}:{config.CONTEXT_BROKER_PORT}/ngsi-ld/v1/entities/"


def _test_get_image(url: str, path: str):
    r = requests.get(url)
    assert r.ok, r.text
    with open(path, "rb") as f:
        hash_local = hashlib.sha256(f.read()).hexdigest()
    hash_api = hashlib.sha256(r.content).hexdigest()
    assert hash_local == hash_api

def test_docs():
    r = requests.get(API_URL + "docs")
    assert r.ok, r.text
    

def test_redoc():
    r = requests.get(API_URL + "redoc")
    assert r.ok, r.text
  

def test_post_get():
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
    assert r.ok, r.text
    img_id = r.json()
    with open(config.IMG_FACES_ID_PATH, "w") as f:
        f.write(img_id)
    assert isinstance(img_id, str)
    assert img_id.startswith("urn:ngsi-ld:Image:")

    # Get entity from context broker
    r = requests.get(BROKER_URL + img_id)
    assert r.ok, r.text
    entity = r.json()
    assert entity["source"]["value"] == data["source"]
    assert entity["purpose"]["value"] == data["purpose"]
    assert entity["width"]["value"] == img_w
    assert entity["height"]["value"] == img_h
    assert entity["type"] == "Image"

    # Get image from API
    _test_get_image(API_URL + img_id, config.IMG_FACES_PATH)
    
#     # Get image by url
#     _test_get_image(ent["url"]["value"])
        
#     def test_upload_file(self):
#         # Create a non image file
#         with tempfile.TemporaryFile() as fp:
#             fp.write(b"not an image")

#             # Post file with fake mime
#             files = {"file": ("test.png", fp, "image/png")}
#             data = {
#                 "source": "test_source",
#                 "purpose": "test_purpose"
#             }
#             headers = {"accept": "application/json"}
#             r = requests.post(self.URL, headers=headers, data=data, files=files)
#             self.assertEqual(r.status_code, 422)

#             # Post non image file 
#             files = {"file": ("test.png", fp, "text/plain")}
#             data = {
#                 "source": "test_source",
#                 "purpose": "test_purpose"
#             }
#             headers = {"accept": "application/json"}
#             r = requests.post(self.URL, headers=headers, data=data, files=files)
#             self.assertEqual(r.status_code, 415)

#             # Post without files
#             data = {
#                 "source": "test_source",
#                 "purpose": "test_purpose"
#             }
#             headers = {"accept": "application/json"}
#             r = requests.post(self.URL, headers=headers, data=data)
#             self.assertEqual(r.status_code, 422)
        
#         # Post a large file
#         with tempfile.TemporaryFile() as fp:
#             # Write n bytes to file
#             for i in range(int(config.LARGE_FILE_BSIZE)):
#                 fp.write(b"h")
#             print(fp.tell())
#             # Post the file
#             files = {"file": ("test.png", fp, "text/plain")}
#             data = {
#                 "source": "test_source",
#                 "purpose": "test_purpose"
#             }
#             headers = {"accept": "application/json"}
#             r = requests.post(self.URL, headers=headers, data=data, files=files)
#             self.assertEqual(r.status_code, 413)



# if __name__ == "__main__":
#     unittest.main()