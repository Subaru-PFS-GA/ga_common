import os
import numpy as np

from pfs.ga.common.selection import ConeSelection

from ..test_base import TestBase

class ConeSelectionTest(TestBase):
    def test_apply(self):
        obs = self.load_test_observation()
        ra, dec = obs.get_coords()
        sel = ConeSelection(
            center = (ra.mean(), dec.mean()),
            radius = 10.0
        )
        mask = sel.apply(obs)
        self.assertTrue(np.any(mask))