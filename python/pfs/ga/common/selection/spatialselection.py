import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u

from ..util import *
from .util import *
from ..data import Catalog
from .selection import Selection

class SpatialSelection(Selection):
    """
    Implements a class to select objects within a specified sky region.
    """

    def __init__(
        self,
        orig = None
    ):
        super().__init__(orig=orig)

        self._validate()

    def _validate(self):
        pass

    def _get_coords(self, catalog: Catalog):
        ra, dec = catalog.get_coords()
        coords = SkyCoord(ra * u.deg, dec * u.deg)
        return coords
    
        