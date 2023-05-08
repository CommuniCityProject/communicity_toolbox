import unittest
from datetime import datetime

import numpy as np
from ngsildclient import Entity

from toolbox import DataModels
from toolbox.Context.entity_parser import (create_entity, create_random_id,
                                           get_entity_field, parse_entity,
                                           set_entity_field)
from toolbox.Structures import (BoundingBox, Emotion, Gender, Image, Keypoints,
                                SegmentationMask)


class TestEntityParser(unittest.TestCase):

    def test_create_random_id(self):
        id = create_random_id()
        self.assertTrue(id.startswith("urn:ngsi-ld:"))

        id = create_random_id("Person")
        self.assertTrue(id.startswith("urn:ngsi-ld:Person:"))

        id = create_random_id(prefix="urn:ngsi:")
        self.assertTrue(id.startswith("urn:ngsi:"))

        id = create_random_id("Person", prefix="urn:ngsi:")
        self.assertTrue(id.startswith("urn:ngsi:Person:"))

        id_a = create_random_id()
        for i in range(10):
            id_b = create_random_id()
            self.assertNotEqual(id_a, id_b)
            id_a = id_b

        id_a = create_random_id(uuid4=True, shortener=True)
        for i in range(10):
            id_b = create_random_id(uuid4=True, shortener=True)
            self.assertNotEqual(id_a, id_b)
            id_a = id_b

        id_a = create_random_id(uuid4=True, shortener=False)
        for i in range(10):
            id_b = create_random_id(uuid4=True, shortener=False)
            self.assertNotEqual(id_a, id_b)
            id_a = id_b

    def test_set_entity_field(self):
        entity = Entity("test", "1234")

        values = {
            "test_int": 1,
            "test_float": 1.1,
            "test_str": "test",
            "test_bool": True,
            "bounding_box": BoundingBox(.1, .2, .3, .4),
            "emotion": Emotion.HAPPINESS,
            "gender": Gender.FEMALE,
            "keypoints": Keypoints.COCOKeypoints(np.ones((17, 3))),
            "segmentation_mask": SegmentationMask(np.ones((100, 100)))
        }

        for k, v in values.items():
            set_entity_field(entity, v, k)

        self.assertEqual(entity["test_int"]["value"], values["test_int"])
        self.assertEqual(entity["test_float"]["value"], values["test_float"])
        self.assertEqual(entity["test_str"]["value"], values["test_str"])
        self.assertEqual(entity["test_bool"]["value"], values["test_bool"])
        self.assertEqual(entity["emotion"]["value"], str(values["emotion"]))
        self.assertEqual(entity["gender"]["value"], str(values["gender"]))
        self.assertEqual(entity["bounding_box"]["value"],
                         values["bounding_box"].serialize())
        self.assertEqual(entity["segmentation_mask"]["value"],
                         values["segmentation_mask"].serialize())

    def test_create_entity(self):
        face = DataModels.Face(
            id="123",
            image="urn:ngsi-ld:Image:456",
            bounding_box=BoundingBox(.1, .2, .3, .4),
            detectionConfidence=0.5,
            age=20,
            gender=Gender.FEMALE,
            genderConfidence=0.6,
            emotion=Emotion.HAPPINESS,
            emotionConfidence=0.7,
            features=[1, 2, 3],
            recognized=True,
            recognizedPerson="test_person",
            featuresAlgorithm="test_algorithm",
            recognizedDistance=0.8,
            # recognition_domain="test_domain"
        )
        ent = create_entity(face)
        self.assertEqual(ent["id"], f"urn:ngsi-ld:Face:{face.id}")
        self.assertEqual(ent.type, face.type)
        self.assertEqual(ent["image"]["object"], face.image)
        self.assertEqual(ent["boundingBox"]["value"],
                         face.bounding_box.serialize())
        self.assertEqual(ent["detectionConfidence"]["value"],
                         face.detection_confidence)
        self.assertEqual(ent["age"]["value"], face.age)
        self.assertEqual(ent["gender"]["value"], str(face.gender))
        self.assertEqual(ent["genderConfidence"]["value"],
                         face.gender_confidence)
        self.assertEqual(ent["emotion"]["value"], str(face.emotion))
        self.assertEqual(ent["features"]["value"], face.features)
        self.assertEqual(ent["recognized"]["value"], face.recognized)
        self.assertEqual(ent["recognizedPerson"]["value"],
                         face.recognized_person)
        self.assertEqual(ent["featuresAlgorithm"]
                         ["value"], face.features_algorithm)
        self.assertEqual(ent["recognizedDistance"]
                         ["value"], face.recognized_distance)
        self.assertRaises(KeyError, lambda: ent["recognitionDomain"])

        mask = DataModels.InstanceSegmentation(
            id="123",
            image="urn:ngsi-ld:Image:456",
            mask=SegmentationMask(np.ones((100, 100))),
            bounding_box=BoundingBox(.1, .2, .3, .4),
            label="test_label",
            label_id=1,
            confidence=0.8
        )
        ent = create_entity(mask)
        self.assertEqual(
            ent["id"], f"urn:ngsi-ld:InstanceSegmentation:{mask.id}")
        self.assertEqual(ent.type, mask.type)
        self.assertEqual(ent["image"]["object"], mask.image)
        self.assertEqual(ent["mask"]["value"], mask.mask.serialize())
        self.assertEqual(ent["boundingBox"]["value"],
                         mask.bounding_box.serialize())
        self.assertEqual(ent["label"]["value"], mask.label)
        self.assertEqual(ent["labelId"]["value"], mask.label_id)
        self.assertEqual(ent["confidence"]["value"], mask.confidence)

        kp = DataModels.PersonKeyPoints(
            id="123",
            image="urn:ngsi-ld:Image:456",
            boundingBox=BoundingBox(.1, .2, .3, .4),
            confidence=0.8,
            keypoints=Keypoints.COCOKeypoints(np.ones((17, 3)))
        )
        ent = create_entity(kp)
        self.assertEqual(
            ent["id"], f"urn:ngsi-ld:PersonKeyPoints:{kp.id}")
        self.assertEqual(ent.type, kp.type)
        self.assertEqual(ent["image"]["object"], kp.image)
        self.assertEqual(ent["boundingBox"]["value"],
                         kp.bounding_box.serialize())
        self.assertEqual(ent["confidence"]["value"], kp.confidence)
        self.assertEqual(ent["keypoints"]["value"], kp.keypoints.serialize())

    def test_get_entity_field(self):
        test_int = 1
        test_float = 1.1
        test_str = "test"
        test_bool = True
        test_bounding_box = BoundingBox(.1, .2, .3, .4)
        test_emotion = Emotion.HAPPINESS
        test_gender = Gender.FEMALE
        test_keypoints = Keypoints.COCOKeypoints(np.ones((17, 3)))
        test_segmentation_mask = SegmentationMask(np.ones((100, 100)))
        test_date = datetime(2000, 1, 1, 0, 0, 0, 0)
        test_image = Image("path", np.zeros(
            (100, 100, 3), dtype=np.uint8), id="test_image")
        test_list = [1, 2, 3, 4, 5]

        get_int = get_entity_field(test_int, int)
        get_float = get_entity_field(test_float, float)
        get_str = get_entity_field(test_str, str)
        get_bool = get_entity_field(test_bool, bool)
        get_bounding_box = get_entity_field(
            test_bounding_box.serialize(), BoundingBox)
        get_emotion = get_entity_field(str(test_emotion), Emotion)
        get_gender = get_entity_field(str(test_gender), Gender)
        get_keypoints = get_entity_field(
            test_keypoints.serialize(), Keypoints.COCOKeypoints)
        get_segmentation_mask = get_entity_field(
            test_segmentation_mask.serialize(), SegmentationMask)
        get_date = get_entity_field(
            {"@value": "2000-01-01T00:00:00Z"}, datetime)
        get_image = get_entity_field(test_image.serialize(), Image)
        get_np = get_entity_field(test_list, np.ndarray)

        self.assertEqual(get_int, test_int)
        self.assertEqual(get_float, test_float)
        self.assertEqual(get_str, test_str)
        self.assertEqual(get_bool, test_bool)
        self.assertEqual(get_bounding_box, test_bounding_box)
        self.assertEqual(get_emotion, test_emotion)
        self.assertEqual(get_gender, test_gender)
        self.assertEqual(get_keypoints, test_keypoints)
        self.assertEqual(get_segmentation_mask, test_segmentation_mask)
        self.assertEqual(get_date, test_date)
        self.assertEqual(get_image, test_image)
        np.testing.assert_array_equal(get_np, np.array(test_list))

        self.assertIsInstance(get_int, int)
        self.assertIsInstance(get_float, float)
        self.assertIsInstance(get_str, str)
        self.assertIsInstance(get_bool, bool)
        self.assertIsInstance(get_bounding_box, BoundingBox)
        self.assertIsInstance(get_emotion, Emotion)
        self.assertIsInstance(get_gender, Gender)
        self.assertIsInstance(get_keypoints, Keypoints.COCOKeypoints)
        self.assertIsInstance(get_segmentation_mask, SegmentationMask)
        self.assertIsInstance(get_date, datetime)
        self.assertIsInstance(get_image, Image)
        self.assertIsInstance(get_np, np.ndarray)

    def test_parse_entity(self):
        face = DataModels.Face(
            image="urn:ngsi-ld:Image:456",
            bounding_box=BoundingBox(.1, .2, .3, .4),
            detectionConfidence=0.8,
            age=20,
            gender=Gender.FEMALE,
            genderConfidence=0.9,
            emotion=Emotion.HAPPINESS,
            emotionConfidence=0.7,
            features=[1, 2, 3, 4, 5],
            recognitionDomain="test_domain",
            recognized=True,
            recognized_person="test_person",
            features_algorithm="test_algorithm",
            recognized_distance=0.9
        )
        face.dateObserved = face.dateObserved.replace(microsecond=0)
        ent = create_entity(face)
        parsed_face = parse_entity(ent, DataModels.Face)

        self.assertIsInstance(parsed_face, DataModels.Face)
        self.assertEqual(parsed_face, face)

        mask = DataModels.InstanceSegmentation(
            image="urn:ngsi-ld:Image:456",
            mask=SegmentationMask(np.ones((100, 100))),
            bounding_box=BoundingBox(.1, .2, .3, .4),
            label="test_label",
            label_id=1,
            confidence=0.8
        )
        mask.dateObserved = mask.dateObserved.replace(microsecond=0)
        ent = create_entity(mask)
        parsed_mask = parse_entity(ent, DataModels.InstanceSegmentation)
        self.assertIsInstance(parsed_mask, DataModels.InstanceSegmentation)
        self.assertEqual(parsed_mask, mask)

        kp = DataModels.PersonKeyPoints(
            image="urn:ngsi-ld:Image:456",
            boundingBox=BoundingBox(.1, .2, .3, .4),
            confidence=0.8,
            keypoints=Keypoints.COCOKeypoints(np.ones((17, 3)))
        )
        kp.dateObserved = kp.dateObserved.replace(microsecond=0)
        ent = create_entity(kp)
        parsed_kp = parse_entity(ent, DataModels.PersonKeyPoints)
        self.assertIsInstance(parsed_kp, DataModels.PersonKeyPoints)
        self.assertEqual(parsed_kp, kp)

        self.assertRaises(
            TypeError, lambda: parse_entity(ent, DataModels.Face))


if __name__ == "__main__":
    unittest.main()
