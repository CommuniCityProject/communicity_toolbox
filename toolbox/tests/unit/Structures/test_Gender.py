import unittest

from toolbox.Structures import Gender


class TestGender(unittest.TestCase):

    def test_init(self):
        gen = Gender.FEMALE
        self.assertIs(gen, Gender.FEMALE)
    
    def test_str(self):
        gen = Gender.FEMALE
        self.assertEqual(str(gen), "FEMALE")
    
    def test_from_str(self):
        gen = Gender["FEMALE"]
        self.assertIs(gen, Gender.FEMALE)


if __name__ == '__main__':
    unittest.main()
