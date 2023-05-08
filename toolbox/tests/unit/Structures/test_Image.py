import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from toolbox.Structures import Image

URL_IMG = "https://upload.wikimedia.org/wikipedia/commons/d/d6/Wikipedia-logo-v2-en.png"
URL_IMG_SIZE = (1920, 2204)  # (width, height)


class TestImage(unittest.TestCase):

    def test_init(self):
        # Test default
        img = Image()
        self.assertEqual(img.path, Path(""))
        self.assertRaises(BaseException, lambda: img.image)
        self.assertRaises(BaseException, lambda: img.height)
        self.assertRaises(BaseException, lambda: img.width)
        self.assertEqual(img.id, "")

        # Test Path
        img = Image(path=Path("path/to/image.jpg"))
        self.assertEqual(img.path, Path("path/to/image.jpg"))
        self.assertIsInstance(img.path, Path)

        img = Image(path="path/to/image.jpg")
        self.assertEqual(img.path, Path("path/to/image.jpg"))
        self.assertIsInstance(img.path, Path)

        # Test URL
        img = Image(path="https://path/to/image.jpg")
        self.assertEqual(img.path, "https://path/to/image.jpg")
        self.assertIsInstance(img.path, str)

        img = Image(path="http://path/to/image.jpg")
        self.assertEqual(img.path, "http://path/to/image.jpg")
        self.assertIsInstance(img.path, str)

    def test_init_image_path(self):
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png") as f:
            np_img = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
            cv2.imwrite(f.name, np_img)
            img = Image(path=f.name, id="urn:ngsi-ld:Image:001")
            self.assertEqual(img.height, 100)
            self.assertEqual(img.width, 200)
            self.assertTrue(np.array_equal(img.image, np_img))
            self.assertEqual(img.id, "urn:ngsi-ld:Image:001")
            self.assertEqual(img.path, Path(f.name))
            self.assertIsInstance(img.path, Path)

    def test_init_numpy(self):
        np_img = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
        img = Image(
            path="path/to/image.jpg",
            image=np_img,
            id="urn:ngsi-ld:Image:001"
        )
        self.assertEqual(img.height, 100)
        self.assertEqual(img.width, 200)
        self.assertTrue(np.array_equal(img.image, np_img))
        self.assertEqual(img.id, "urn:ngsi-ld:Image:001")
        self.assertEqual(img.path, Path("path/to/image.jpg"))
        self.assertIsInstance(img.path, Path)

    def test_init_image_url(self):
        img = Image(path=URL_IMG, id="urn:ngsi-ld:Image:001")
        self.assertEqual(img.height, URL_IMG_SIZE[1])
        self.assertEqual(img.width, URL_IMG_SIZE[0])
        self.assertEqual(img.id, "urn:ngsi-ld:Image:001")
        self.assertEqual(img.path, URL_IMG)
        self.assertIsInstance(img.path, str)

    def test_from_url(self):
        img = Image.from_url(URL_IMG)
        self.assertEqual(img.height, URL_IMG_SIZE[1])
        self.assertEqual(img.width, URL_IMG_SIZE[0])
        self.assertEqual(img.id, "")
        self.assertEqual(img.path, URL_IMG)
        self.assertIsInstance(img.path, str)

        # Test from a path
        self.assertRaises(BaseException, lambda: Image.from_url(
            Path("/path/to/image.jpg")))

    def test_from_path(self):
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png") as f:
            np_img = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
            cv2.imwrite(f.name, np_img)
            img = Image.from_path(f.name)
            self.assertEqual(img.height, 100)
            self.assertEqual(img.width, 200)
            self.assertTrue(np.array_equal(img.image, np_img))
            self.assertEqual(img.id, "")
            self.assertEqual(img.path, Path(f.name))
            self.assertIsInstance(img.path, Path)

        # Test from a URL
        self.assertRaises(BaseException, lambda: Image.from_path(URL_IMG))

    def serialize_deserialize(self):
        img = Image(
            path="path/to/image.jpg",
            width=200,
            height=100,
            id="urn:ngsi-ld:Image:001"
        )
        img_dict = img.serialize()
        self.assertEqual(img, Image.deserialize(img_dict))

    def test_eq(self):
        self.assertEqual(
            Image(
                path="path/to/image.jpg",
                width=200,
                height=100,
                id="urn:ngsi-ld:Image:001"
            ),
            Image(
                path="path/to/image.jpg",
                width=200,
                height=100,
                id="urn:ngsi-ld:Image:001"
            )
        )
        self.assertNotEqual(
            Image(
                path="path/to/imago.jpg",
                width=200,
                height=100,
                id="urn:ngsi-ld:Image:001"
            ),
            Image(
                path="path/to/image.jpg",
                width=200,
                height=100,
                id="urn:ngsi-ld:Image:001"
            )
        )
        self.assertNotEqual(
            Image(
                path="path/to/image.jpg",
                width=201,
                height=100,
                id="urn:ngsi-ld:Image:001"
            ),
            Image(
                path="path/to/image.jpg",
                width=200,
                height=100,
                id="urn:ngsi-ld:Image:001"
            )
        )
        self.assertNotEqual(
            Image(
                path="path/to/image.jpg",
                width=200,
                height=101,
                id="urn:ngsi-ld:Image:001"
            ),
            Image(
                path="path/to/image.jpg",
                width=200,
                height=100,
                id="urn:ngsi-ld:Image:001"
            )
        )
        self.assertNotEqual(
            Image(
                path="path/to/image.jpg",
                width=200,
                height=100,
                id="urn:ngsi-ld:Image:002"
            ),
            Image(
                path="path/to/image.jpg",
                width=200,
                height=100,
                id="urn:ngsi-ld:Image:001"
            )
        )
        self.assertNotEqual(
            Image(
                path="path/to/image.jpg",
                width=200,
                height=100,
                id="urn:ngsi-ld:Image:001",
                image=np.zeros((100, 200, 3), dtype=np.uint8)
            ),
            Image(
                path="path/to/image.jpg",
                width=200,
                height=100,
                id="urn:ngsi-ld:Image:001",
                image=np.ones((100, 200, 3), dtype=np.uint8)
            )
        )


if __name__ == '__main__':
    unittest.main()
