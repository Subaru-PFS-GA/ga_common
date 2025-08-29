import unittest
import os
import tempfile
import numpy as np
import yaml
import commentjson as json
from pfs.ga.common.config import Config, Lambda

class DummyConfig(Config):
    def __init__(self, a: int = 1, b: str = "test", c: float = 2.0, arr: np.ndarray = np.array([1,2,3]), lam: Lambda = None):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.arr = arr
        self.lam = lam

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config_dict = {
            "a": 10,
            "b": "hello",
            "c": 3.14,
            "arr": [4,5,6],
            "lam": "lambda x: x + 1"
        }

    def test_to_dict_and_from_dict(self):
        cfg = DummyConfig()
        cfg.load(self.config_dict)
        d = cfg.to_dict()
        self.assertEqual(d["a"], 10)
        self.assertEqual(d["b"], "hello")
        self.assertEqual(d["c"], 3.14)
        self.assertEqual(d["arr"], [4,5,6])
        self.assertEqual(cfg.lam(2), 3)

        # Test from_dict classmethod
        cfg2 = DummyConfig.from_dict(self.config_dict)
        self.assertEqual(cfg2.a, 10)
        self.assertEqual(cfg2.b, "hello")
        self.assertEqual(cfg2.c, 3.14)
        self.assertTrue(np.array_equal(cfg2.arr, np.array([4,5,6])))
        self.assertEqual(cfg2.lam(2), 3)

    def test_repr(self):
        cfg = DummyConfig()
        self.assertIsInstance(repr(cfg), str)

    def test_save_and_load_json(self):
        cfg = DummyConfig()
        cfg.load(self.config_dict)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            cfg.save(tmp.name)
            tmp.close()
            loaded = DummyConfig.from_file(tmp.name)
            self.assertEqual(loaded.a, 10)
            self.assertEqual(loaded.b, "hello")
            self.assertEqual(loaded.c, 3.14)
            self.assertTrue(np.array_equal(loaded.arr, np.array([4,5,6])))
            os.unlink(tmp.name)

    def test_save_and_load_yaml(self):
        cfg = DummyConfig()
        cfg.load(self.config_dict)
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
            cfg.save(tmp.name)
            tmp.close()
            loaded = DummyConfig.from_file(tmp.name)
            self.assertEqual(loaded.a, 10)
            self.assertEqual(loaded.b, "hello")
            self.assertEqual(loaded.c, 3.14)
            self.assertTrue(np.array_equal(loaded.arr, np.array([4,5,6])))
            os.unlink(tmp.name)

    def test_load_py_file(self):
        py_content = "config = {'a': 42, 'b': 'py', 'c': 1.23, 'arr': [7,8,9], 'lam': 'lambda x: x*2'}"
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp:
            tmp.write(py_content)
            tmp.close()
            loaded = DummyConfig.from_file(tmp.name)
            self.assertEqual(loaded.a, 42)
            self.assertEqual(loaded.b, "py")
            self.assertEqual(loaded.c, 1.23)
            self.assertTrue(np.array_equal(loaded.arr, np.array([7,8,9])))
            self.assertEqual(loaded.lam(3), 6)
            os.unlink(tmp.name)

    def test_merge_dict(self):
        a = {"x": 1, "y": {"z": 2}}
        b = {"y": {"z": 3}, "w": 4}
        merged = Config._Config__merge_dict(a, b, ignore_collisions=True)
        self.assertEqual(merged["y"]["z"], 3)
        self.assertEqual(merged["x"], 1)
        self.assertEqual(merged["w"], 4)

    def test_collision(self):
        a = {"x": 1}
        b = {"x": 2}
        with self.assertRaises(ValueError):
            Config._Config__merge_dict(a, b, ignore_collisions=False)

    def test_copy_dict(self):
        a = {"x": 1, "y": {"z": 2}, "l": [ {"a": 3}, {"b": 4} ]}
        copied = Config._Config__copy_dict(a)
        self.assertEqual(copied, a)
        self.assertIsNot(copied, a)
        self.assertIsNot(copied["y"], a["y"])
        self.assertIsNot(copied["l"][0], a["l"][0])

if __name__ == "__main__":
    unittest.main()