import unittest
from copy import deepcopy

from toolbox.Structures import Instance


class TestInstance(unittest.TestCase):

    def test_init(self):
        inst = Instance()
    
    def test_set_dict(self):
        # Nested dicts
        values = {
            "key1": "value1",
            "key2": "value2",
            "key3": {
                "key4": "value4",
                "key5": "value5",
            },
            "key6": {
                "key7": {
                    "key8": "value8"
                }
            }
        }
        inst = Instance().set_dict(values)
        self.assertEqual(inst.key1, "value1")
        self.assertEqual(inst.key2, "value2")
        self.assertIsInstance(inst.key3, dict)
        self.assertIsInstance(inst.key6, dict)
        self.assertIsInstance(inst.key6["key7"], dict)
        self.assertEqual(inst.key3["key4"], "value4")
        self.assertEqual(inst.key3["key5"], "value5")
        self.assertEqual(inst.key6["key7"]["key8"], "value8")

        inst = Instance(values)
        self.assertEqual(inst.key1, "value1")
        self.assertEqual(inst.key2, "value2")
        self.assertIsInstance(inst.key3, dict)
        self.assertIsInstance(inst.key6, dict)
        self.assertIsInstance(inst.key6["key7"], dict)
        self.assertEqual(inst.key3["key4"], "value4")
        self.assertEqual(inst.key3["key5"], "value5")
        self.assertEqual(inst.key6["key7"]["key8"], "value8")
        
        # Nested Instances
        values = {
            "key1": "value1",
            "key2": "value2",
            "key3": Instance({
                "key4": "value4",
                "key5": "value5",
            }),
            "key6": Instance({
                "key7": Instance({
                    "key8": "value8"
                })
            })
        }
        inst = Instance().set_dict(values)
        self.assertEqual(inst.key1, "value1")
        self.assertEqual(inst.key2, "value2")
        self.assertIsInstance(inst.key3, Instance)
        self.assertIsInstance(inst.key6, Instance)
        self.assertIsInstance(inst.key6.key7, Instance)
        self.assertEqual(inst.key3.key4, "value4")
        self.assertEqual(inst.key3.key5, "value5")
        self.assertEqual(inst.key6.key7.key8, "value8")

    def test_set(self):
        values = {
            "key1": "value1",
            "key2": "value2",
            "key3": {
                "key4": "value4",
                "key5": "value5",
            },
            "key6": {
                "key7": {
                    "key8": "value8"
                }
            }
        }
        inst = Instance(values)
        inst.set("key1", "value10")
        self.assertEqual(inst.key1, "value10")
        inst.key1 = "value11"
        self.assertEqual(inst.key1, "value11")
        self.assertEqual(inst._fields["key1"], "value11")
        
    def test_set_get(self):
        inst = Instance()

        inst.set("key1", "value")
        
        # Modify existing key
        inst.set("key1", "value1")
        
        # Add new keys with the return value
        inst = inst.set("key2", 2).set("key3", 3.3)

        # Get existing keys
        self.assertEqual(inst.get("key1"), "value1")
        self.assertEqual(inst.get("key2"), 2)
        self.assertEqual(inst.get("key3"), 3.3)

        # Get non-existing keys
        self.assertIsNone(inst.get("key4"))
        self.assertEqual(inst.get("ke4", 4), 4)

    def test_get_attr(self):
        inst = Instance().set("key1", "value1").set("key2", "value2")
        self.assertEqual(inst.key1, "value1")
        self.assertEqual(inst.key2, "value2")
        self.assertRaises(AttributeError, lambda: inst.key3)
    
    def test_get_item(self):
        inst = Instance().set("key1", "value1").set("key2", "value2")
        self.assertEqual(inst["key1"], "value1")
        self.assertEqual(inst["key2"], "value2")
        self.assertRaises(KeyError, lambda: inst["key3"])

    def test_fields(self):
        inst = Instance().set("key1", "value1").set("key2", "value2")
        self.assertEqual(inst.fields, ["key1", "key2"])
    
    def test_has(self):
        inst = Instance().set("key1", "value1").set("key2", "value2")
        self.assertTrue(inst.has("key1"))
        self.assertTrue(inst.has("key2"))
        self.assertFalse(inst.has("key3"))
    
    def test_remove(self):
        inst = Instance().set("key1", "value1").set("key2", "value2")
        inst.remove("key1")
        self.assertFalse(inst.has("key1"))
        self.assertTrue(inst.has("key2"))
        self.assertRaises(KeyError, lambda: inst.remove("key3"))
    
    def test_eq(self):
        # Same
        self.assertEqual(
            Instance().set("key1", "value1").set("key2", "value2"),
            Instance().set("key1", "value1").set("key2", "value2"),
        )
        # Different order
        self.assertEqual(
            Instance().set("key1", "value1").set("key2", "value2"),
            Instance().set("key2", "value2").set("key1", "value1"),
        )
        # Different values
        self.assertNotEqual(
            Instance().set("key1", "value1").set("key2", "value2"),
            Instance().set("key1", "value2").set("key2", "value2"),
        )
        # Different keys
        self.assertNotEqual(
            Instance().set("key1", "value1").set("key2", "value2"),
            Instance().set("key3", "value1").set("key2", "value2"),
        )
        # Nested instances
        self.assertEqual(
            Instance().set("I1", Instance().set("k1", "v1")),
            Instance().set("I1", Instance().set("k1", "v1")),
        )
        self.assertNotEqual(
            Instance().set("I1", Instance().set("k1", "v1")),
            Instance().set("I1", Instance().set("k1", "v2")),
        )
        # Nested dicts
        values = {
            "key1": "value1",
            "key2": "value2",
            "key3": {
                "key4": "value4",
                "key5": "value5",
            },
            "key6": {
                "key7": {
                    "key8": "value8"
                }
            }
        }
        inst_a = Instance().set_dict(values)
        inst_b = Instance().set_dict(deepcopy(values))
        inst_b.key6["key7"]["key9"] = "value90"
        self.assertNotEqual(inst_a, inst_b)

        # Nested Instances
        values = {
            "key1": "value1",
            "key2": "value2",
            "key3": Instance({
                "key4": "value4",
                "key5": "value5",
            }),
            "key6": Instance({
                "key7": Instance({
                    "key8": "value8"
                })
            })
        }
        inst_a = Instance().set_dict(values)
        inst_b = Instance().set_dict(deepcopy(values))
        inst_b.key6.key7.key8 = "value90"
        self.assertNotEqual(inst_a, inst_b)


if __name__ == '__main__':
    unittest.main()
