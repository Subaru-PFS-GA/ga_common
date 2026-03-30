import os
import numpy as np
import matplotlib.pyplot as plt

from pfs.ga.common.projection import Pointing, WcsProjection
from pfs.ga.common.diagram import CCD

from ..test_base import TestBase

class CCDTest(TestBase):
    def test_plot_catalog(self):
        obs = self.load_test_observation()
        f, ax = self.get_test_plot()

        ccd, _ = self.get_test_ccd()
        obs.plot(ax, ccd)

        self.save_fig(f)

    def test_plot_observation(self):
        obs = self.load_test_observation()
        f, ax = self.get_test_plot()

        ccd, _ = self.get_test_ccd()
        obs.plot(ax, ccd)

        self.save_fig(f)
