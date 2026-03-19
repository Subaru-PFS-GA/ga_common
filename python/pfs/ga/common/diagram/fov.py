from collections.abc import Iterable
import numpy as np
import matplotlib.pyplot as plt
from astropy.visualization.wcsaxes.core import WCSAxes
from astropy.coordinates import SkyCoord, SkyOffsetFrame
import astropy.units as u

from . import styles
from .spatialdiagram import SpatialDiagram
from .radecaxis import RaDecAxis
from ..util import normalize_coords, denormalize_coords

class FOV(SpatialDiagram):
    """
    A plot of the field of view of some instrument assuming a valid WCS projection
    defined in the form of WCSAxes or WCSAxesSubplot.
    """

    def __init__(self, projection=None, orig=None):
        ra = RaDecAxis('RA', invert=True)
        dec = RaDecAxis('Dec')
        axes = [ ra, dec ]
        super().__init__(axes, projection=projection, orig=orig)

        self._validate()

    def _validate(self):
        pass

    def _get_native_frame(self, native_frame=None):
        return native_frame if native_frame is not None else 'world'
    
    def apply(self, ax: plt.Axes):
        super().apply(ax)
        ax.set_aspect('equal', adjustable='datalim')

    def plot_radial_profile(self, ax: plt.Axes, profile, R=1, **kwargs):
        # TODO: add default style
        ell = profile.get_ellipse(R)
        return self.plot(ax, ell, native_frame='world', **kwargs)
    
    def plot_ellipse(self, ax: plt.Axes, *center, radius=None, ellipticity=None, posang=None,
                     resolution=None, fmt=None,
                     scalex=True, scaley=True, **kwargs):
        """
        Plot an ellipse assuming the projection set in the initializer
        """

        ctype, (ra, dec) = normalize_coords(*center)
        radius = radius if radius is not None else 1.0      # arc min
        ellipticity = ellipticity if ellipticity is not None else 0.0
        posang = posang if posang is not None else 0.0      # degree
        resolution = resolution if resolution is not None else 360

        # Calculate the ra and dec (world) coordinates of the ellipse
        A  = radius * 2 * u.arcmin         # full major axis
        e  = ellipticity                   # ellipticity

        a = (A / 2).to(u.deg)            # semi-major axis
        b = a * (1 - e)                  # semi-minor axis

        # Rotated tangent-plane frame
        center = SkyCoord(ra * u.deg, dec * u.deg, frame='icrs')
        offset_frame = SkyOffsetFrame(origin=center, rotation=posang * u.deg)

        # Parametrize the ellipse in the offset frame
        t = np.linspace(0, 2 * np.pi, resolution)
        x = a * np.cos(t)   # along major axis
        y = b * np.sin(t)   # along minor axis

        ellipse_offset = SkyCoord(lon=x, lat=y, frame=offset_frame)

        # Transform back to RA/Dec
        ellipse_icrs = ellipse_offset.transform_to('icrs')

        ra_ellipse  = ellipse_icrs.ra.deg
        dec_ellipse = ellipse_icrs.dec.deg

        # Plot the ellipse
        native_frame = 'world'
        l = super().plot(ax, ra_ellipse, dec_ellipse,
                         fmt=fmt, native_frame=native_frame,
                         scalex=scalex, scaley=scaley,
                         **kwargs)
        return l

    def plot_instrument(self, ax: plt.Axes, instrument, **kwargs):
        instrument.plot_field_of_view(ax, self, **kwargs)