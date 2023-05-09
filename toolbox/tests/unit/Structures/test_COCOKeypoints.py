import unittest

import numpy as np

from toolbox.Structures.Keypoints import COCOKeypoints

NP_KP = np.random.rand(17, 3)
NP_KP[:, -1] = 1.0


class TestCOCOKeypoints(unittest.TestCase):

    def test_init(self):
        kp = COCOKeypoints(NP_KP.copy(), 0.5)

    def test_labels(self):
        kp = COCOKeypoints(NP_KP.copy())
        self.assertEqual(len(COCOKeypoints.labels), 17)
        self.assertEqual(len(kp.labels), 17)

    def test_kp(self):
        kp = COCOKeypoints(NP_KP.copy())
        self.assertTrue(np.array_equal(kp.keypoints, NP_KP))
        kp.keypoints[0, 0] = 10
        self.assertEqual(kp.keypoints[0, 0], 10)

    def test_confidence_threshold(self):
        kp = COCOKeypoints(NP_KP.copy(), 0.5)
        self.assertEqual(kp.confidence_threshold, 0.5)
        kp.confidence_threshold = 0.6
        self.assertEqual(kp.confidence_threshold, 0.6)

    def test_named_keypoints(self):
        kp = COCOKeypoints(NP_KP.copy())
        named = kp.named_keypoints
        self.assertEqual(len(named), 17)
        self.assertEqual(
            list(named.keys()),
            COCOKeypoints.labels
        )
        self.assertTrue(np.array_equal(named[kp.labels[0]], NP_KP[0]))

        kp.keypoints[0, 0] = 10
        named = kp.named_keypoints
        self.assertEqual(named[kp.labels[0]][0], 10)

        kp.keypoints[-1, 0] = 20
        named = kp.named_keypoints
        self.assertEqual(named[kp.labels[-1]][0], 20)

    def test_visible_keypoints(self):
        kp = COCOKeypoints(NP_KP.copy(), 0.5)
        visible = kp.visible_keypoints
        self.assertEqual(len(visible), 17)
        self.assertEqual(
            list(visible.keys()),
            COCOKeypoints.labels
        )

        kp.keypoints[0, 0] = 10
        visible = kp.visible_keypoints
        self.assertEqual(visible[kp.labels[0]][0], 10)

        kp.keypoints[-1, 0] = 20
        visible = kp.visible_keypoints
        self.assertEqual(visible[kp.labels[-1]][0], 20)

        kp.keypoints[0, -1] = 0.4
        visible = kp.visible_keypoints
        self.assertEqual(len(visible), 16)
        self.assertNotIn(kp.labels[0], visible.keys())

        kp.confidence_threshold = 0.4
        visible = kp.visible_keypoints
        self.assertEqual(len(visible), 17)
        self.assertIn(kp.labels[0], visible.keys())

    def test_serialize_deserialize(self):
        kp = COCOKeypoints(NP_KP.copy(), confidence_threshold=0.5)
        ser = kp.serialize()
        des = COCOKeypoints.deserialize(ser)
        self.assertTrue(np.array_equal(kp.keypoints, des.keypoints))

    def test_from_named_keypoints(self):
        kp = COCOKeypoints(NP_KP.copy(), confidence_threshold=0.5)
        named = kp.named_keypoints
        new_kp = COCOKeypoints.from_named_keypoints(named)
        self.assertTrue(np.array_equal(kp.keypoints, new_kp.keypoints))

    def test_from_absolute_keypoints(self):
        h, w = (100, 200)
        abs_kp = NP_KP.copy()
        abs_kp[:, 0] = abs_kp[:, 0] * w
        abs_kp[:, 1] = abs_kp[:, 1] * h
        kp = COCOKeypoints.from_absolute_keypoints(abs_kp, w, h)
        np.testing.assert_almost_equal(kp.keypoints, NP_KP)

    def test_str(self):
        kp = COCOKeypoints(NP_KP.copy())
        self.assertTrue(str(kp))

    def test_eq(self):
        kp = COCOKeypoints(NP_KP.copy(), 0.5)
        kp2 = COCOKeypoints(NP_KP.copy(), 0.5)
        self.assertEqual(kp, kp2)
        kp2.keypoints[0, 0] = 10
        self.assertNotEqual(kp, kp2)

        kp2 = COCOKeypoints(NP_KP.copy(), 0.5)
        self.assertEqual(kp, kp2)
        kp2.confidence_threshold = 0.6
        self.assertNotEqual(kp, kp2)

    def test_len(self):
        kp = COCOKeypoints(NP_KP.copy(), 0.1)
        self.assertEqual(len(kp), 17)
        kp = COCOKeypoints(NP_KP.copy(), 2)
        self.assertEqual(len(kp), 0)


if __name__ == '__main__':
    unittest.main()
