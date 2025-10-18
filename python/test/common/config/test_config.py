import unittest
import os
import tempfile
import numpy as np
import yaml
import commentjson as json
from typing import List, Dict

from pfs.ga.common.config import Config, Lambda

class DummyConfig(Config):
    def __init__(self, a: int = 1, b: str = "test", c: float = 2.0, arr: np.ndarray = np.array([1,2,3]), lam: Lambda = None):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.arr = arr
        self.lam = lam

class SubConfig(Config):
    def __init__(self):
        super().__init__()

        self.c = None
        self.d = None

class MainConfig(Config):
    def __init__(self,
                 sub: SubConfig = SubConfig(),
                 entries: List[SubConfig] = None,
                 dicts: Dict[str, SubConfig] = None):
        
        super().__init__()

        self.a = None
        self.b = None
        self.sub = sub
        self.entries = entries
        self.dicts = dicts

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config_dict = {
            "a": 10,
            "b": "hello",
            "c": 3.14,
            "arr": [4,5,6],
            "lam": "lambda x: x + 1"
        }

    def get_test_dict(self):
        return {
            'a': 1,
            'b': 2,
            'sub': { 'c': 3, 'd': 4 },
            'entries': [
                { 'c': 5, 'd': 6 },
                { 'c': 7, 'd': 8 }
            ],
            'dicts': {
                'one': { 'c': 9, 'd': 10 },
                'two': { 'c': 11, 'd': 12 }
            }
        }

    def get_test_config(self):
        c = MainConfig()
        c.a = 1
        c.b = 2
        c.sub.c = 3
        c.sub.d = 4
        c.entries = [ SubConfig(), SubConfig() ]
        c.entries[0].c = 5
        c.entries[0].d = 6
        c.entries[1].c = 7
        c.entries[1].d = 8
        c.dicts = { 'one': SubConfig(), 'two': SubConfig() }
        c.dicts['one'].c = 9
        c.dicts['one'].d = 10
        c.dicts['two'].c = 11
        c.dicts['two'].d = 12

        return c

    def test_init(self):
        c = self.get_test_config()

    def test_config_to_class(self):
        d = self.get_test_dict()
        c = Config._Config__config_to_class(MainConfig, d)

        self.assertIsInstance(c, MainConfig)
        self.assertEqual(c.a, 1)
        self.assertEqual(c.b, 2)
        self.assertIsInstance(c.sub, SubConfig)
        self.assertEqual(c.sub.c, 3)
        self.assertEqual(c.sub.d, 4)
        self.assertIsInstance(c.entries, list)
        self.assertEqual(len(c.entries), 2)
        self.assertIsInstance(c.entries[0], SubConfig)
        self.assertEqual(c.entries[0].c, 5)
        self.assertEqual(c.entries[0].d, 6)
        self.assertIsInstance(c.dicts, dict)
        self.assertEqual(len(c.dicts), 2)
        self.assertIsInstance(c.dicts['one'], SubConfig)
        self.assertEqual(c.dicts['one'].c, 9)
        self.assertEqual(c.dicts['one'].d, 10)

    def test_config_to_dict(self):
        c = self.get_test_config()
        d = Config._Config__save_config_to_dict(c)
        
        self.assertEqual(d, self.get_test_dict())

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

    def test_save(self):
        c = self.get_test_config()
        c.save('./tmp/test/config.yaml')
        c.save('./tmp/test/config.json')

    def test_load(self):
        c = MainConfig()
        c.load('./data/test/config_01.yaml')
        
        c = MainConfig()
        c.load('./data/test/config_01.json')

        c = MainConfig()
        c.load('./data/test/config_01.py')

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