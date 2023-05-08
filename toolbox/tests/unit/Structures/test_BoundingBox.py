import unittest
import numpy as np

from toolbox.Structures import BoundingBox


class TestBoundingBox(unittest.TestCase):

    def test_init(self):
        xmin = 0.1
        ymin = 0.2
        xmax = 0.9
        ymax = 0.6
        bb = BoundingBox(xmin, ymin, xmax, ymax)
        self.assertEqual(bb.xmin, xmin)
        self.assertEqual(bb.ymin, ymin)
        self.assertEqual(bb.xmax, xmax)
        self.assertEqual(bb.ymax, ymax)

    def test_get_width(self):
        # Create a bounding box
        xmin = 0.3
        ymin = 0.2
        xmax = 0.7
        ymax = 0.7
        bb = BoundingBox(xmin, ymin, xmax, ymax)
        # Test relative coordinates
        w = bb.get_width()
        np.testing.assert_almost_equal(w, 0.4)
        # Test absolute coordinates
        wa = bb.get_width(absolute=True, image_width=10)
        np.testing.assert_almost_equal(wa, 4)
        # Test absolute type
        self.assertIsInstance(wa, int)

    def test_get_height(self):
        # Create a bounding box
        xmin = 0.3
        ymin = 0.2
        xmax = 0.7
        ymax = 0.7
        bb = BoundingBox(xmin, ymin, xmax, ymax)
        # Test relative coordinates
        h = bb.get_height()
        np.testing.assert_almost_equal(h, 0.5)
        # Test absolute coordinates
        ha = bb.get_height(absolute=True, image_height=10)
        np.testing.assert_almost_equal(ha, 5)
        # Test absolute type
        self.assertIsInstance(ha, int)

    def test_get_center_x(self):
        # Create a bounding box
        xmin = 0.3
        ymin = 0.2
        xmax = 0.7
        ymax = 0.7
        bb = BoundingBox(xmin, ymin, xmax, ymax)
        # Test relative coordinates
        cx = bb.get_center_x()
        np.testing.assert_almost_equal(cx, 0.5)
        # Test absolute coordinates
        cxa = bb.get_center_x(absolute=True, image_width=10)
        np.testing.assert_almost_equal(cxa, 5)
        # Test rounding
        xmax = 0.8
        bb = BoundingBox(xmin, ymin, xmax, ymax)
        # Relative
        cx = bb.get_center_x()
        np.testing.assert_almost_equal(cx, 0.55)
        # Absolute
        cxa = bb.get_center_x(absolute=True, image_width=10)
        np.testing.assert_almost_equal(cxa, round(5.5))
        # Test absolute type
        self.assertIsInstance(cxa, int)

    def test_get_center_y(self):
        # Create a bounding box
        xmin = 0.3
        ymin = 0.2
        xmax = 0.7
        ymax = 0.7
        bb = BoundingBox(xmin, ymin, xmax, ymax)
        # Test relative coordinates
        cy = bb.get_center_y()
        np.testing.assert_almost_equal(cy, 0.45)
        # Test absolute coordinates
        cya = bb.get_center_y(absolute=True, image_height=10)
        np.testing.assert_almost_equal(cya, round(4.5))
        # Test non rounding
        ymax = 0.8
        bb = BoundingBox(xmin, ymin, xmax, ymax)
        # Relative
        cy = bb.get_center_y()
        np.testing.assert_almost_equal(cy, 0.5)
        # Absolute
        cya = bb.get_center_y(absolute=True, image_height=10)
        np.testing.assert_almost_equal(cya, 5)
        # Test absolute type
        self.assertIsInstance(cya, int)

    def test_get_area(self):
        # Create a bounding box
        xmin = 0.3
        ymin = 0.2
        xmax = 0.7
        ymax = 0.7
        bb = BoundingBox(xmin, ymin, xmax, ymax)
        # Test relative value
        a = bb.get_area()
        np.testing.assert_almost_equal(a, 0.2)
        # Test absolute value
        aa = bb.get_area(absolute=True, image_height=8, image_width=10)
        np.testing.assert_almost_equal(aa, 16)
        # Test absolute type
        self.assertIsInstance(aa, int)

    def test_get_xyxy(self):
        # Create a bounding box
        xmin = 0.3
        ymin = 0.2
        xmax = 0.7
        ymax = 0.7
        bb = BoundingBox(xmin, ymin, xmax, ymax)
        # Test relative coordinates
        xyxy = bb.get_xyxy()
        self.assertIsInstance(xyxy, np.ndarray)
        np.testing.assert_array_almost_equal(
            xyxy,
            np.array([0.3, 0.2, 0.7, 0.7])
        )
        # Test absolute coordinates
        xyxy = bb.get_xyxy(absolute=True, image_height=8, image_width=10)
        self.assertIsInstance(xyxy, np.ndarray)
        np.testing.assert_array_equal(
            xyxy,
            np.array([3, round(1.6), 7, round(5.6)])
        )

    def test_get_xywh(self):
        # Create a bounding box
        xmin = 0.3
        ymin = 0.2
        xmax = 0.7
        ymax = 0.7
        bb = BoundingBox(xmin, ymin, xmax, ymax)
        # Test relative coordinates
        xywh = bb.get_xywh()
        self.assertIsInstance(xywh, np.ndarray)
        np.testing.assert_array_almost_equal(
            xywh,
            np.array([0.5, 0.45, 0.4, 0.5])
        )
        # Test absolute coordinates
        xyxy = bb.get_xywh(absolute=True, image_height=8, image_width=10)
        self.assertIsInstance(xyxy, np.ndarray)
        np.testing.assert_array_equal(
            xyxy,
            np.array([5, round(3.6), 4, 4])
        )

    def test_from_absolute(self):
        xmin = 3
        ymin = 2
        xmax = 7
        ymax = 7
        img_w = 10
        img_h = 8
        bb = BoundingBox.from_absolute(xmin, ymin, xmax, ymax, img_w, img_h)
        np.testing.assert_almost_equal(bb.xmin, 0.3)
        np.testing.assert_almost_equal(bb.ymin, 0.25)
        np.testing.assert_almost_equal(bb.xmax, 0.7)
        np.testing.assert_almost_equal(bb.ymax, 0.875)

    def test_from_xywh(self):
        # From relative
        cx = 0.5
        cy = 0.45
        w = 0.4
        h = 0.5
        bb = BoundingBox.from_xywh(cx, cy, w, h)
        np.testing.assert_almost_equal(bb.xmin, 0.3)
        np.testing.assert_almost_equal(bb.ymin, 0.2)
        np.testing.assert_almost_equal(bb.xmax, 0.7)
        np.testing.assert_almost_equal(bb.ymax, 0.7)
        # From absolute
        cx = 5
        cy = 4.5
        w = 4
        h = 5
        img_w = 10
        img_h = 8
        bb = BoundingBox.from_xywh(cx, cy, w, h, True, img_w, img_h)
        np.testing.assert_almost_equal(bb.xmin, 0.3)
        np.testing.assert_almost_equal(bb.ymin, 0.25)
        np.testing.assert_almost_equal(bb.xmax, 0.7)
        np.testing.assert_almost_equal(bb.ymax, 0.875)

    def test_crop_image(self):
        # Create a bounding box
        xmin = 0.3
        ymin = 0.2
        xmax = 0.7
        ymax = 0.7
        bb = BoundingBox(xmin, ymin, xmax, ymax)
        # Create a random image
        img_w = 10
        img_h = 8
        img_3 = np.random.random((img_h, img_w, 3))
        img_1 = np.random.random((img_h, img_w))
        # Crop the images
        img_3_crop = bb.crop_image(img_3)
        img_1_crop = bb.crop_image(img_1)
        # Assert crops
        np.testing.assert_array_equal(
            img_3_crop,
            img_3[round(1.6):round(5.6), 3:7, :],
            strict=True
        )
        np.testing.assert_array_equal(
            img_1_crop,
            img_1[round(1.6):round(5.6), 3:7],
            strict=True
        )
        # Test copy
        c_img_3 = img_3.copy()
        img_3_crop[:] = 0
        np.testing.assert_array_equal(
            c_img_3,
            img_3,
            strict=True
        )
        # Test type
        self.assertTrue(
            bb.crop_image(np.zeros((3,3,3), dtype=np.uint8)).dtype == np.uint8
        )

        # Create bounding box surpassing image limits
        bb = BoundingBox(0,0,1,1)
        img = np.zeros((100,100))
        img_crop = bb.crop_image(img)
        self.assertEqual(img_crop.shape, img.shape)
        bb = BoundingBox(-1,-1,2,2)
        self.assertEqual(img_crop.shape, img.shape)
        
    def test_scale(self):
        xmin = 0.305
        ymin = 0.475
        xmax = 0.355
        ymax = 0.525

        bb = BoundingBox(xmin, ymin, xmax, ymax)
        
        # Test same scale
        bb_s = bb.scale(2)
        np.testing.assert_almost_equal(bb_s.xmin, 0.28)
        np.testing.assert_almost_equal(bb_s.xmax, 0.38)
        np.testing.assert_almost_equal(bb_s.ymin, 0.45)
        np.testing.assert_almost_equal(bb_s.ymax, 0.55)

        # Test different scale
        bb_s = bb.scale((2, 1.5))
        np.testing.assert_almost_equal(bb_s.xmin, 0.28)
        np.testing.assert_almost_equal(bb_s.xmax, 0.38)
        np.testing.assert_almost_equal(bb_s.ymin, 0.4625)
        np.testing.assert_almost_equal(bb_s.ymax, 0.5375)

    def test_is_empty_bool(self):
        self.assertTrue( BoundingBox(.0,.0,.0,.0).is_empty())
        self.assertTrue( BoundingBox(.1,.0,.2,.0).is_empty())
        self.assertTrue( BoundingBox(.0,.1,.0,.2).is_empty())
        self.assertTrue( BoundingBox(.1,.1,.1,.1).is_empty())
        self.assertFalse(BoundingBox(.1,.2,.3,.4).is_empty())

        self.assertFalse(BoundingBox(.0,.0,.0,.0))
        self.assertFalse(BoundingBox(.1,.0,.2,.0))
        self.assertFalse(BoundingBox(.0,.1,.0,.2))
        self.assertFalse(BoundingBox(.1,.1,.1,.1))
        self.assertTrue( BoundingBox(.1,.2,.3,.4))

    def test_eq(self):
        self.assertEqual(   BoundingBox(.1,.2,.3,.4), BoundingBox(.1,.2,.3,.4))
        self.assertNotEqual(BoundingBox(.1,.2,.3,.4), BoundingBox(.0,.2,.3,.4))
        self.assertNotEqual(BoundingBox(.1,.2,.3,.4), BoundingBox(.1,.0,.3,.4))
        self.assertNotEqual(BoundingBox(.1,.2,.3,.4), BoundingBox(.1,.2,.0,.4))
        self.assertNotEqual(BoundingBox(.1,.2,.3,.4), BoundingBox(.1,.2,.3,.0))

    def test_serialize_deserialize(self):
        bb = BoundingBox(.1,.2,.3,.4)
        ser = bb.serialize()
        des = BoundingBox.deserialize(ser)
        self.assertEqual(bb.xmin, des.xmin)
        self.assertEqual(bb.ymin, des.ymin)
        self.assertEqual(bb.xmax, des.xmax)
        self.assertEqual(bb.ymax, des.ymax)


if __name__ == '__main__':
    unittest.main()
