import os
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u

from pfs.ga.common.diagram import FOV

from ..test_base import TestBase

class FOVTest(TestBase):
    def test_plot(self):
        obs = self.load_test_observation()
        ra, dec = obs.get_coords()
        p = self.get_projection(obs)
        fov = FOV(projection=p)
        
        f, ax = self.get_test_plot(projection=p.wcs)
        fov.plot(ax, ra, dec, native_frame='world')
        ax.grid()

        self.save_fig(f)

    def test_plot_world(self):
        obs = self.load_test_observation()
        ra, dec = obs.get_coords()
        p = self.get_projection(obs)
        fov = FOV(projection=p)
        
        f, ax = self.get_test_plot(projection=p.wcs)
        fov.plot(ax, ra, dec, native_frame='world')
        ax.grid()
        
        self.save_fig(f)

    def test_plot_pixel(self):
        obs = self.load_test_observation()
        ra, dec = obs.get_coords()
        p = self.get_projection(obs)
        fov = FOV(projection=p)
        
        f, ax = self.get_test_plot(projection=p.wcs)
        fov.plot(ax, ra, dec, native_frame='pixel')
        ax.grid()
        
        self.save_fig(f)

    def test_scatter(self):
        obs = self.load_test_observation()
        ra, dec = obs.get_coords()
        p = self.get_projection(obs)
        fov = FOV(projection=p)
        
        f, ax = self.get_test_plot(projection=p.wcs)
        fov.scatter(ax, ra, dec, native_frame='world')
        ax.grid()
        
        self.save_fig(f)

    def test_scatter_world(self):
        obs = self.load_test_observation()
        ra, dec = obs.get_coords()
        p = self.get_projection(obs)
        fov = FOV(projection=p)
        
        f, ax = self.get_test_plot(projection=p.wcs)
        fov.scatter(ax, ra, dec, native_frame='world')
        ax.grid()
        
        self.save_fig(f)

    def test_scatter_pixel(self):
        obs = self.load_test_observation()
        ra, dec = obs.get_coords()
        p = self.get_projection(obs)
        fov = FOV(projection=p)
        
        f, ax = self.get_test_plot(projection=p.wcs)
        fov.scatter(ax, ra, dec, native_frame='pixel')
        ax.grid()
        
        self.save_fig(f)

    def test_plot_observation(self):
        obs = self.load_test_observation()
        p = self.get_projection(obs)
        fov = FOV(projection=p)

        f, ax = self.get_test_plot(projection=p.wcs)
        obs._plot_spatial(ax, fov)

        self.save_fig(f)

    def test_plot_radial_profile(self):
        self.skipTest('Not implemented yet')

    def test_plot_ellipse(self):
        obs = self.load_test_observation()
        p = self.get_projection(obs)
        fov = FOV(projection=p)

        f, ax = self.get_test_plot(projection=p.wcs)
        obs._plot_spatial(ax, fov, scalex=True, scaley=True)
        fov.plot(ax, [p.pointing.ra], [p.pointing.dec], marker='o', c='red', ms=10, native_frame='world',
                 scalex=False, scaley=False)
        fov.plot_ellipse(ax, p.pointing.ra, p.pointing.dec, radius=30, ellipticity=0.5, posang=-45,
                         scalex=False, scaley=False, color='red', ls='-', linewidth=3)

        ax.coords['ra'].set_format_unit(u.deg)
        ax.coords['dec'].set_format_unit(u.deg)
        ax.coords['ra'].set_major_formatter('d.dddd')
        ax.coords['dec'].set_major_formatter('d.dddd')

        f.tight_layout()

        self.save_fig(f)