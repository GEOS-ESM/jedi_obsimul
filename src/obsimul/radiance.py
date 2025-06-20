"""

Implement the generic GEOVAL class which primiraly converts GEOS samplying output for the IODA geometry, 
producing a IODA compliant file that can be used by JEDI to computate radiances. This packages defines the base class to
be specialized for each observinbg platform.

"""
import numpy  as np
import xarray as xr
from   datetime import datetime, timedelta

from .geoval          import GEOVAL, GeovalError, wind_direction
from pyobs.constants import *

Sensors = [ 'airs_aqua','amsr2_gcom-w1','amsua_aqua', 'amsua_metopb', 
            'amsua_n15','amsua_n18', 'amsua_n19', 'atms_n20', 'atms_npp',
            'avhrr3_metop-b', 'avhrr3_n18', 'avhrr3_n19',
            'cris-fsr_n20', 'cris_fsr_npp', 'gmi_gpm', 'iasi_metop-b',
            'mhs_metop-b', 'mhs_n19', 'ssmis_f17' ]

class RADIANCE(GEOVAL):

    def populate(self):
        """
        Create GEOVAL object for radiances. On input,
 
        """

        nr = self.nr

        # Initialize surface area fractions
        self['water_area_fraction'] = nr.FROCEAN + nr.FRLAKE
        self['land_area_fraction']  = nr.FRLAND
        self['ice_area_fraction']   = nr.FRSEAICE + nr.FRLANDICE
        self.zero_sfcVars('cloud_volume_fraction_in_atmosphere_layer')

        # Adjust water_area_fraction where sea ice exists
        I = (nr.FRSEAICE>0.0)&(self.water_area_fraction>0.0)
        self.water_area_fraction[I] -= nr.FRSEAICE[I]
            
        # Surface snow area fraction
        self.zero_sfcVars('surface_snow_area_fraction')

        I = (nr.SNOWDP>0.0001)&(nr.SNOWDP<1000000.)
        self.surface_snow_area_fraction[I] = self.ice_area_fraction[I] + self.land_area_fraction[I]
        self.ice_area_fraction[I]          = 0.0  # Snow takes over ice
        self.land_area_fraction[I]         = 0.0  # Snow takes over land
        
        # Consistency check: total area fraction must be 1
        tot_frac = self.water_area_fraction.values.copy()
        tot_frac[I] = self.water_area_fraction[I]        + self.land_area_fraction[I] \
                    + self.surface_snow_area_fraction[I] + self.ice_area_fraction[I]

        if tot_frac.max() > 1.0001:
            raise GeovalError('Total area fraction does not add to 1 somewhere, please check')

        # Surface temperature
        self['surface_temperature_where_sea']                = nr.TS
        self['skin_temperature_at_surface_where_sea']        = nr.TS
        self['surface_temperature_where_land']               = nr.TS
        self['skin_temperature_at_surface_where_land']       = nr.TS
        self['surface_temperature_where_ice']                = nr.TS
        self['skin_temperature_at_surface_where_ice']        = nr.TS
        self['surface_temperature_where_snow']               = nr.TS
        self['skin_temperature_at_surface_where_snow']       = nr.TS
        self['skin_temperature_at_surface']                  = nr.TS
        self['air_temperature_at_two_meters_above_surface']  = nr.T2M 
        self['water_vapor_mixing_ratio_wrt_moist_air_at_2m'] = nr.Q2M 

        # Surface wind speed and direction
        # IMPORTANT: New NR files may have these varaibles as u10N, noit u10M
        u10 = nr.U10M   # Shape should be (nlocs,)
        v10 = nr.V10M   # Shape should be (nlocs,)
        
        # Compute surface wind speed (element-wise)
        self['surface_wind_speed'] = xr.ufuncs.sqrt(xr.ufuncs.maximum(u10**2 + v10**2, 0.9e-4))

        # Compute wind direction for locations where wind speed is above a threshold
        self.zero_sfcVars('surface_wind_from_direction')

        # Mask for wind speeds greater than the threshold
        I = self.surface_wind_speed > 0.001

        # Apply the wind direction calculation only to the masked locations
        self.surface_wind_from_direction[I] = wind_direction(u10[I], v10[I])

        self['leaf_area_index'] = nr.LAI

        # Normalize wind direction to be within 0-360 degrees
        # QUESTION: Is this needed?
        #self.surface_wind_from_direction[self.surface_wind_from_direction < 0] += 360.0
        
        # Translate constants for soil and vegetation types to CRTM conventions
        igbp_to_gfs  = [4, 1, 5, 2, 3, 8, 9, 6, 6, 7, 8, 12, 7, 12, 13, 11, 0, 10, 10, 11]
        soil_to_crtm = [1, 1, 4, 2, 2, 8, 7, 2, 6, 5, 2, 3, 8, 1, 6, 9]

        self['land_type_index_NPOESS']   = _toCRTM(self.vtype,igbp_to_gfs) 
        self['vegetation_type_index']    = _toCRTM(self.vtype,igbp_to_gfs)
        self['soil_type']                = _toCRTM(self.stype,soil_to_crtm)  
        self['vegetation_area_fraction'] = self.vfrac

        # Other land surface related variables directly GEOS NR
        self['soil_temperature'] = nr.TSOIL1
        self['volume_fraction_of_condensed_water_in_soil'] = nr.GWETTOP   # Check unit
        self['average_surface_temperature_within_field_of_view'] = nr.TS  # Temporary
        self['surface_snow_thickness'] = nr.SNOWDP  # Check unit

        self['tropopause_pressure'] = nr.TROPPB  # Temporary. Not used in CRTM? GEOS may have it
        
        # Geopotential height conversion
        self['surface_geopotential_height'] = nr.PHIS / MAPL_GRAV  # phis[m2 sec-2] --> geo.pot.height[m]
        self['surface_geometric_height'] = self.surface_geopotential_height * 6371000.0 / (6371000.0 - self.surface_geopotential_height)
        self['height_above_mean_sea_level_at_surface'] = self.surface_geopotential_height \
                                                         * 6371000.0 / (6371000.0 - self.surface_geopotential_height)
  
        # Atmospheric profile info
        self['air_temperature'] = nr.T
    
        # Humidity mixing ratio calculation: are these really the same?
        self['humidity_mixing_ratio']                = 1000.0 * nr.QV / (1.0 - nr.QV)
        self['water_vapor_mixing_ratio_wrt_dry_air'] = 1000.0 * nr.QV / (1.0 - nr.QV)
       
        # Temporary values for ozone and CO2 mole fractions (adjust as needed)
        self['mole_fraction_of_ozone_in_air']          = nr.O3  
        self['mole_fraction_of_carbon_dioxide_in_air'] = nr.CO2  

        # QUESTION: what about the cloud condensate for all sky simulations

def _toCRTM(gfs,gfs_to_crtm):
    """
    Translate GFS indices to CRTM indices.
    """
    N = np.isnan(gfs.values)
    I = np.zeros(gfs.shape).astype('int')
    I[~N] = gfs.values[~N].astype('int') - 1 # NaNs will have zeros
    #print( 'Indices:', I.min(), I.max(), len(gfs_to_crtm))
    x = np.array([ gfs_to_crtm[i] for i in I])
    x[N] = 255 # unclassified, this means NaNs
    return xr.DataArray(x, dims=['nlocs'], attrs=gfs.attrs)

    
def CLI_radiances():

    """
    Parses command line and write files with resulting GEOVAL file for radiances.
    """

    from optparse        import OptionParser

    format = 'NETCDF4'
    outFile = 'geoval_ioda.nc4'

#   Parse command line options
#   --------------------------
    parser = OptionParser(usage="Usage: %prog [OPTIONS] nr_filename sfc_filename\n"+\
                                "where: \n"+
                                "   nr_filename         IODA sampled GEOS Nature Run file name\n"+\
                                "   sfc_filename        GFS lat-lon file with vegetation/soil type\n",
                          version='1.0.0' )

    parser.add_option("-o", "--output", dest="outFile", default=outFile,
              help="Output NetCDF file name (default=%s)"\
                          %outFile )

    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose",
                      help="Verbose mode.")

    (options, args) = parser.parse_args()

    if len(args) == 2 :
        nrFile, sfcFiles = args
    else:
        parser.error("must have 2 or 4 arguments: stnFile inDataset [iso_t1 iso_t2]")


    # Lazy-load Nature Run file
    # -------------------------
    nr = xr.open_dataset(nr_filename,engine='netcdf4')

    # Lazy-load GF surface file
    # -------------------------
    sfc = xr.open_dataset(nr_filename,engine='netcdf4')

    # Instantiate RADIANCE object
    # ---------------------------
    gv = RADIANCE(nr,sfc)

    # Populate with NR data...
    # ------------------------
    gv.populate()

    # Write out compressed netcdf-4 file
    # ----------------------------------
    gv.write(options.outFile,verbose=options.verbose)


#..............................................................................................

if __name__ == "__main__":

    CLI_radiances()


    
