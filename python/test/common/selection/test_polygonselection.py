import os
import numpy as np
from shapely.geometry import Polygon

from pfs.ga.common.photometry import Color
from pfs.ga.common.selection import PolygonSelection

from ..test_base import TestBase

class PolygonSelectionTest(TestBase):
    def get_test_points(self):
        return [[0.1, 16.1],
                [2.0, 16.1],
                [2.0, 23.5],
                [0.1, 23.5],
                [0.1, 16.1]]

    def test_apply_observation(self):
        cmd, photometry = self.get_test_cmd()
        obs = self.load_test_observation()
        points = self.get_test_points()

        sel = PolygonSelection(cmd.axes, points)
        mask = sel.apply(obs)
        self.assertEqual(1, mask.ndim)
