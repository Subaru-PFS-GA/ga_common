import os

from pfs.ga.common.io import GaiaReader

from ..test_base import TestBase

class GaiaReaderTest(TestBase):
    def test_cone_search(self):
        r = GaiaReader()
        obs = r.cone_search([10, 20], 1)

        self.assertEqual((4, 24), obs.data.shape)

        self.assertTrue('gaia' in obs.photometry)
        self.assertTrue('g' in obs.photometry['gaia'].magnitudes)