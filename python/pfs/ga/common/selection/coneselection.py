import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u

from ..util import *
from .util import *
from ..data import Catalog
from .spatialselection import SpatialSelection

class ConeSelection(SpatialSelection):
    """
    Implements a class to select objects within a specified sky region.
    """

    def __init__(
        self,
        center,
        radius,
        orig = None
    ):
        super().__init__(orig=orig)

        if not isinstance(orig, ConeSelection):
            self.__center = center
            self.__radius = radius
        else:
            self.__center = center or orig.__center
            self.__radius = radius or orig.__radius

        self._validate()

    def _validate(self):
        pass

    def apply(self, catalog: Catalog, mask=None):
        coords = self._get_coords(catalog)
        
        ra, dec = self.__center
        center = SkyCoord(ra * u.deg, dec * u.deg)

        # Calculate the separation
        separation = coords.separation(center)

        # Make the cut
        radius = self.__radius * u.arcmin
        return separation <= radius
        