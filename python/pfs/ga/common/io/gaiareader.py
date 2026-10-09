import os
import logging
from astroquery.utils.tap.conn.tapconn import TapConn
from astropy.coordinates import SkyCoord
import astropy.units as u

from ..util.args import *
from ..data import Observation
from .catalogserializer import CatalogSerializer

logger = logging.getLogger(__name__)

MIRROR = False

if MIRROR:
    from astroquery.gaia import GaiaClass
    _gaia_tap_handler = TapConn(
        ishttps=True,
        host='gaia.aip.de',
        server_context='/tap',
        tap_context='',
        upload_context='Upload',
        table_edit_context='TableTool',
        data_context='data',
        datalink_context='datalink',
    )
    _gaia_tap_handler._TapConn__postHeaders['Accept'] = '*/*'
    Gaia = GaiaClass(tap_plus_conn_handler=_gaia_tap_handler)
else:
    from astroquery.gaia import Gaia


def _gaia_login():
    """
    Log in to the Gaia archive if a credentials file exists (username on the first
    line, password on the second). The path is taken from `GAIA_CREDENTIALS` or
    defaults to `~/.gaia_credentials`. Continues anonymously if not available.
    """

    path = os.path.expanduser(os.environ.get('GAIA_CREDENTIALS', '~/.gaia_credentials'))
    if not os.path.isfile(path):
        return

    try:
        if not getattr(Gaia, '_PfsLoggedIn', False):
            Gaia.login(credentials_file=path)
            Gaia._PfsLoggedIn = True
            logger.info('Logged in to the Gaia archive.')
    except Exception as ex:
        logger.warning(f'Could not log in to the Gaia archive, continuing anonymously: {ex}')

class GaiaReader(CatalogSerializer):
    def __init__(self,
                 catalog_name='gaia',
                 limits=None,
                 mask=None,
                 orig=None,
                 **kwargs):

        filters = {
            "gaia_g": dict(
                mag = "obs_gaia_g",
                flux = "flux_gaia_g",
                flux_err = "err_flux_gaia_g",
            ),
            "gaia_bp": dict(
                mag = "obs_gaia_bp",
                flux = "flux_gaia_bp",
                flux_err = "err_flux_gaia_bp",
            ),
            "gaia_rp": dict(
                mag = "obs_gaia_rp",
                flux = "flux_gaia_rp",
                flux_err = "err_flux_gaia_rp",
            )
        }
        
        CatalogSerializer.__init__(self,
                                   catalog_name=catalog_name,
                                   filters=filters,
                                   # bands=bands,
                                   # photometry=photometry,
                                   limits=limits,
                                   orig=orig)

        if not isinstance(orig, GaiaReader):
            pass
        else:
            pass

    def _create_catalog(self):
        obs = Observation(name=self.catalog_name, frame='icrs', epoch='J2016.0')
        for _, p in self.photometry.items():
            obs.append_photometry(p)
        return obs

    def cone_search(self, pos, rad):
        """
        Run a cone search on the GAIA archive.
        
        Parameters:
        -----------
        pos: `SkyCoord`:
            Cone search center
        rad: `Angle` or `Number`:
            Cone search radius, in arc min if `Number`
        """

        # TODO: bring out parameters like data release etc.
        # TODO: apply filters on query lever rather than post-filtering

        pos = normalize_pos(pos)
        rad = normalize_angle(rad, u.arcmin)

        Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaiadr3.gaia_source"
        Gaia.ROW_LIMIT = -1
        
        query = f"""
            SELECT
                source_id,
                ra, ra_error, dec, dec_error, ref_epoch,
                parallax, parallax_error,
                pm, pmra, pmra_error, pmdec, pmdec_error,
                radial_velocity, radial_velocity_error,
                phot_g_mean_flux, phot_g_mean_flux_error, phot_g_mean_mag,
                phot_bp_mean_flux, phot_bp_mean_flux_error, phot_bp_mean_mag,
                phot_rp_mean_flux, phot_rp_mean_flux_error, phot_rp_mean_mag
            FROM gaiadr3.gaia_source
            WHERE CONTAINS(POINT('ICRS', gaiadr3.gaia_source.ra, gaiadr3.gaia_source.dec),
                           CIRCLE('ICRS', {pos.ra.degree:0.8f}, {pos.dec.degree:0.8f}, {rad.degree:0.8f})) = 1;"""
        print(query)
        _gaia_login()
        job = Gaia.launch_job_async(query, dump_to_file=False, output_format='votable')
        gaia = job.get_results()
        df = gaia.to_pandas()
        df.rename(inplace=True,
            columns={
                'SOURCE_ID': 'targetid',
                'ra': 'RA',
                'dec': 'Dec',
                'ra_error': 'err_RA',
                'dec_error': 'err_Dec',
                'ref_epoch': 'epoch',
                'parallax': 'parallax',
                'parallax_error': 'err_parallax',
                'pm': 'pm',
                'pmra': 'pmra',
                'pmra_error': 'err_pmra',
                'pmdec': 'pmdec',
                'pmdec_error': 'err_pmdec',
                'radial_velocity': 'rv',
                'radial_velocity_error': 'err_rv',
                'phot_g_mean_mag': 'gaia_g',
                'phot_g_mean_flux': 'flux_gaia_g',
                'phot_g_mean_flux_error': 'err_flux_gaia_g',
                'phot_bp_mean_mag': 'gaia_bp',
                'phot_bp_mean_flux': 'flux_gaia_bp',
                'phot_bp_mean_flux_error': 'err_flux_gaia_bp',
                'phot_rp_mean_mag': 'gaia_rp',
                'phot_rp_mean_flux': 'flux_gaia_rp',
                'phot_rp_mean_flux_error': 'err_flux_gaia_rp'
            })

        self._read_photometry(df)

        obs = self._create_catalog()
        obs._set_data(df)
        obs._set_photometry(self.photometry)

        # If limits are defined, apply them
        # TODO: this could be done from the SQL query
        if self.limits is not None:
            obs = obs.apply_magnitude_limits(self.limits)

        return obs

    def select_guide_stars(self, pos, rad, mag_min=12.0, mag_max=21.0):
        """
        Select stars from GAIA that can be used as astrometric guides
        """

        pos = normalize_pos(pos)
        rad = normalize_angle(rad, u.arcmin)

        Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaiadr3.gaia_source"
        Gaia.ROW_LIMIT = -1
        
        query = f"""
            SELECT
                source_id,
                ra, ra_error, dec, dec_error, ref_epoch,
                parallax, parallax_error,
                pm, pmra, pmra_error, pmdec, pmdec_error,
                phot_g_mean_flux, phot_g_mean_flux_error,
                phot_bp_mean_flux, phot_bp_mean_flux_error,
                phot_rp_mean_flux, phot_rp_mean_flux_error
            FROM gaiadr3.gaia_source
            WHERE CONTAINS(POINT('ICRS', gaiadr3.gaia_source.ra, gaiadr3.gaia_source.dec),
                           CIRCLE('ICRS', {pos.ra.degree:0.8f}, {pos.dec.degree:0.8f}, {rad.degree:0.8f})) = 1
                  AND pmra IS NOT NULL
                  AND pmdec IS NOT NULL
                  AND parallax IS NOT NULL
                  AND parallax > 0
                  AND astrometric_excess_noise_sig < 2.0
                  AND phot_g_mean_mag BETWEEN {mag_min} AND {mag_max};"""
        print(query)
        _gaia_login()
        job = Gaia.launch_job_async(query, dump_to_file=False, output_format='votable')
        gaia = job.get_results()
        df = gaia.to_pandas()
        df.rename(inplace=True,
            columns={
                'SOURCE_ID': 'targetid',
                'ra': 'RA',
                'dec': 'Dec',
                'ra_error': 'err_RA',
                'dec_error': 'err_Dec',
                'ref_epoch': 'epoch',
                'parallax': 'parallax',
                'parallax_error': 'err_parallax',
                'pm': 'pm',
                'pmra': 'pmra',
                'pmra_error': 'err_pmra',
                'pmdec': 'pmdec',
                'pmdec_error': 'err_pmdec',
                'phot_g_mean_flux': 'flux_gaia_g',
                'phot_g_mean_flux_error': 'err_flux_gaia_g',
                'phot_bp_mean_flux': 'flux_gaia_bp',
                'phot_bp_mean_flux_error': 'err_flux_gaia_bp',
                'phot_rp_mean_flux': 'flux_gaia_rp',
                'phot_rp_mean_flux_error': 'err_flux_gaia_rp'
            })

        self._read_photometry(df)

        obs = self._create_catalog()
        obs._set_data(df)
        obs._set_photometry(self.photometry)

        # If limits are defined, apply them
        # TODO: this could be done from the SQL query
        if self.limits is not None:
            obs = obs.apply_magnitude_limits(self.limits)

        return obs