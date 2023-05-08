import unittest

from toolbox.Structures import Emotion


class TestEmotion(unittest.TestCase):

    def test_init(self):
        emo = Emotion.ANGER
        self.assertIs(emo, Emotion.ANGER)
    
    def test_str(self):
        emo = Emotion.ANGER
        self.assertEqual(str(emo), "ANGER")
    
    def test_from_str(self):
        emo = Emotion["ANGER"]
        self.assertIs(emo, Emotion.ANGER)


if __name__ == '__main__':
    unittest.main()
