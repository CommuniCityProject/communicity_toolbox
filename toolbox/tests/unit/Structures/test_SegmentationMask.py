import unittest
import numpy as np
from pycocotools import mask as pycocotools_mask

from toolbox.Structures import SegmentationMask


RAND_MASK = np.random.randint(0, 2, (100, 200), dtype=np.uint8)

class TestSegmentationMask(unittest.TestCase):

    def test_init(self):
        seg = SegmentationMask(RAND_MASK.copy())
        self.assertTrue(np.array_equal(seg.mask, RAND_MASK))
        self.assertEqual(seg.mask.dtype, np.dtype("bool"))
    
    def test_init_rle(self):
        rle = pycocotools_mask.encode(np.asfortranarray(RAND_MASK))
        seg = SegmentationMask(rle=rle)
        self.assertTrue(np.array_equal(seg.mask, RAND_MASK))
        self.assertEqual(seg.mask.dtype, np.dtype("bool"))

    def test_rle(self):
        seg = SegmentationMask(RAND_MASK.copy())
        rle = seg.rle
        coco_rle = pycocotools_mask.encode(np.asfortranarray(RAND_MASK))
        self.assertEqual(rle["size"], [100, 200])
        self.assertEqual(rle["counts"], coco_rle["counts"])
    
    def test_area(self):
        b_mask = RAND_MASK.astype(bool)
        b_mask[:] = False
        b_mask[:10, :10] = True
        seg = SegmentationMask(b_mask)
        self.assertEqual(seg.area, 100)
    
    def test_width_height(self):
        seg = SegmentationMask(RAND_MASK.copy())
        self.assertEqual(seg.width, 200)
        self.assertEqual(seg.height, 100)
    
    def test_resize(self):
        b_mask = np.zeros((1000, 2000), dtype="bool")
        b_mask[:500, :1000] = True
        seg = SegmentationMask(b_mask)
        seg = seg.resize(200, 100)
        self.assertEqual(seg.width, 200)
        self.assertEqual(seg.height, 100)
        b_mask_res = np.zeros((100, 200), dtype="bool")
        b_mask_res[:50, :100] = True
        np.testing.assert_array_almost_equal(seg.mask, b_mask_res)

    def test_serialize_deserialize(self):
        seg = SegmentationMask(RAND_MASK.copy())
        ser = seg.serialize()
        des = SegmentationMask.deserialize(ser)
        self.assertTrue(np.array_equal(des.mask, RAND_MASK))
    
    def test_str(self):
        seg = SegmentationMask(RAND_MASK.copy())
        self.assertTrue(str(seg))
    
    def test_eq(self):
        seg1 = SegmentationMask(RAND_MASK.copy())
        seg2 = SegmentationMask(RAND_MASK.copy())
        self.assertEqual(seg1, seg2)
        b_mask = RAND_MASK.copy()
        b_mask[1,2] = not RAND_MASK[1,2]
        seg2 = SegmentationMask(b_mask)
        self.assertNotEqual(seg1, seg2)   

if __name__ == '__main__':
    unittest.main()
