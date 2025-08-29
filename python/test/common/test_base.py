import os
from unittest import TestCase
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

import pfs.ga.common
from pfs.ga.common.io import ObservationSerializer
from pfs.ga.common.data import Observation
from pfs.ga.common.photometry import *
from pfs.ga.common.diagram import *
from pfs.ga.common.diagram.diagram import Diagram
from pfs.ga.common.diagram.xyaxis import XYAxis
from pfs.ga.common.projection import Pointing, WcsProjection
from pfs.ga.common.selection import *

class TestBase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        plt.figure(figsize=(10, 6))

        def get_env(k):
            return os.environ[k].strip('"') if k in os.environ else ''

    def get_test_data_file(self, filename):
        return os.path.join(os.path.dirname(pfs.ga.common.__file__), '../../../../data', filename)

    def get_test_temp_file(self, filename):
        return os.path.join(os.path.dirname(pfs.ga.common.__file__), '../../../../tmp', filename)

    def get_filename(self, ext):
        filename = type(self).__name__[:-4] + '_' + self._testMethodName[5:] + ext
        return filename

    def save_fig(self, f=None, filename=None):
        if f is None:
            f = plt
        if filename is None:
            filename = self.get_filename('.png')

        f.tight_layout()
        f.savefig(os.path.join(os.path.dirname(pfs.ga.common.__file__), '../../../../tmp', filename))

    def load_test_observation(self) -> Observation:
        fn =  os.path.join(os.path.dirname(pfs.ga.common.__file__), '../../../../data/test/obs.feather')
        s = ObservationSerializer()
        return s.read(fn)

    def get_test_photometry(self):
        p = Photometry('hsc', latex=r'\mathrm{HSC}\,')
        p.append_magnitude(Magnitude(
            'g',
            latex='g',
            conversion=0.8e33,
            sky=1e5,
            sky_sigma=0,
            zero=0))
        p.append_magnitude(Magnitude(
            'r',
            latex='r',
            conversion=0.8e33,
            sky=5e5,
            sky_sigma=0,
            zero=0))
        p.append_magnitude(Magnitude(
            'i',
            latex='i',
            conversion=0.8e33,
            sky=5e5,
            sky_sigma=0,
            zero=0))
        p.append_magnitude(Magnitude(
            'nb515',
            latex=r'\mathrm{NB}515',
            conversion=1e33,
            sky=1e5,
            sky_sigma=0,
            zero=0.09))

        return p

    def get_test_plot(self, projection=None):
        f, ax = plt.subplots(1, 1, figsize=(3.5, 3.5), dpi=250, subplot_kw=dict(projection=projection))
        return f, ax

    def get_test_diagram(self):
        d = Diagram([XYAxis('x'), XYAxis('y')])
        return d

    def get_test_cmd(self):
        photometry = self.get_test_photometry()
      
        cmd = CMD([
            ColorAxis(
                Color([photometry.magnitudes['g'], photometry.magnitudes['i']]),
                limits=(-1.5, 4.5)),
            MagnitudeAxis(
                photometry.magnitudes['g'],
                limits=(15.5, 24.5))
        ])

        return cmd, photometry

    def get_test_ccd(self):
        photometry = self.get_test_photometry()
      
        ccd = CCD([
            ColorAxis(
                Color([photometry.magnitudes['g'], photometry.magnitudes['i']]),
                limits=(-1.5, 4.5)),
            ColorAxis(
                Color([photometry.magnitudes['nb515'], photometry.magnitudes['g']]),
                limits=(-2, 2))
        ])

        return ccd, photometry

    def get_projection(self, obs):
        ra, dec = obs.get_coords()
        p = WcsProjection(Pointing([ ra.mean(), dec.mean() ], obs_time=datetime(2020, 1, 1, 12, 0, 0)), proj='TAN')
        return p

    def get_test_magnitude_selection(self, cmd):
        return MagnitudeSelection(cmd.axes[1], 18.5, 22.5)

    def get_test_color_selection(self, cmd):
        return ColorSelection(cmd.axes[0], 0, 1.5)
        
    def get_test_selection(self, cmd):
        return AndSelection([
            self.get_test_magnitude_selection(cmd),
            self.get_test_color_selection(cmd)
        ])