"""

Implement the `geovals` class which primiraly converts GEOS samplying output for the IODA geometry, 
producing a IODA compliant file that can be used by JEDI to computate radiances.

"""
import numpy  as np
import xarray as xr
from   datetime import datetime, timedelta

# Default YAML file
Geovals = """

geos_template: 'tbd'
ioda_template: 'tbd'

"""

# --------------------------------------------------------

class GEOVALS(object):

    def __init__ (self, sensor, time, config=None,
                        rootDir='./'):
        """
        Create GEOVAL object.
        """
        self.sensor = sensor
        self.time = time
        self.rootDir = rootDir


        
        
    def populateIODA(self):
        """
        Generate all that is needed to compute radiances.
        """
        
    def writeIODA(self, filename):
        """
        Writeout IODA netCDF file with all variables need for simulating radiances.
        """

#----
class GEOVALS4RAD(GEOVALS):

    def __init__ (self, geos_filename, platform, ioda_template=None):
        """
        Create GEOVAL object.
        """
    def populateIODA(self):
        """
        Generate all that is needed to compute radiances.
        """
        
    def writeIODA(self, filename):
        """
        Writeout IODA netCDF file with all variables need for simulating radiances.
        """

        
