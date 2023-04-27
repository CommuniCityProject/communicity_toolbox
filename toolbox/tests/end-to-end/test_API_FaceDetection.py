import unittest
import requests
import pytest

import config


class test_API_FaceDetection:

    URL = f"http://{config.HOST}:{config.FACE_DETECTION_API_PORT}"

    def test_root(self):
        r = requests.get(self.URL)
        self.assertTrue(r.ok, r.text)

    def test_docs(self):
        r = requests.get(self.URL + "/docs")
        self.assertTrue(r.ok, r.text)
    
    def test_redoc(self):
        r = requests.get(self.URL + "/redoc")
        self.assertTrue(r.ok, r.text)
    
    def test_redoc(self):
        r = requests.get(self.URL + "/redoc")
        self.assertTrue(r.ok, r.text)



if __name__ == "__main__":
    unittest.main()