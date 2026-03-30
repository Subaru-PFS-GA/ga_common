import os
import numpy as np
import matplotlib.pyplot as plt

from pfs.ga.common.selection import AndSelection

from ..test_base import TestBase

class AndSelectionTest(TestBase):
    def test_apply(self):
        cmd, photometry = self.get_test_cmd()
        obs = self.load_test_observation()

        sel = AndSelection([
            self.get_test_magnitude_selection(cmd),
            self.get_test_color_selection(cmd),
        ])

        mask = sel.apply(obs)

