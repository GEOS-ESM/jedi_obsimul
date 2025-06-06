"""

Implement the generic GEOVAL class which primiraly converts GEOS samplying output for the IODA geometry, 
producing a IODA compliant file that can be used by JEDI to computate radiances. This packages defines the base class to
be specialized for each observinbg platform.

"""
import numpy  as np
import xarray as xr
from   datetime import datetime, timedelta

import warnings
import abc

warnings.filterwarnings("ignore", category=FutureWarning)

class GeovalError(Exception):
    """
    Defines general exception errors.
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
    
class GEOVAL(xr.Dataset,abc.ABC):

   def __init__ (self, time, latitude, longitude, pressure_edges, **kwargs):
       """
       Create GEOVAL object as a subclass of xr.Dataset.
       On input, `time`, ..., `pressure_edges` are xr.DataArray objects.
       ANy optional keyword arguments passed down when creating an empty
       `xr.DataSet`.
       """

       # Init as an empty dataset from base class
       # ----------------------------------------
       super.__init__(self,**kwargs)


       # Coordinates
       # -----------
       nlocs, nlevsp1 =  pressure_edges.shape
       self.nlocs, self.nlevs = nlocs, nlevsp1-1
       pressure_mid = (pressure_edges[:-1] + pressure_edges[1:]) / 2.
       self.assign_coords ( time      = time,
                            latitude  = latitude,
                            longitude = longitude,
                            air_pressure = pressure_mid,
                            air_pressure_levels = pressure_edges )
       

   def zero_sfcVars ( self, Vars):
       """
       Add surface variables, initializing them to zero. 
       """
       if isinstance(Vars,str):
           Vars = [Vars,]
       for v in Vars:
           self[v] = xr.DataArray(np.zeros(self.nlocs).astype('float32'),
                                  dims=['nlocs'],
                                  attrs = {'long_name':v.replace('_',' ').capitalize() })
       
   @abc.abstractmethod
   def populate (self, nr):
       """
       Populate GEOVAL data with data from thr Nature RUn dataset `xr`.
     
       """

   def write(self, filename, verbose=False):
       """
       Write out a compressed and chunked netcdf file.
       """

       # Chunks for each dimension
       # --------------------------
       nlocs, nlevs = self.air_pressure.shape
       chunks = dict()
       chunks['nlocs']   = 1000
       chunks['nlevs']   = nlevs
       chunks['nlevsp1'] = nlevs + 1

       # Create encoding for each variable
       # ---------------------------------
       encode = {}
       for v in ds.data_vars:

           chunksizes = [ chunks[d] for d in ds[v].dims ]
           encode[v] = {#'compression':'gzip', 'complevel':2,
                        "zlib": True, "complevel": 2,
                        'chunksizes':chunksizes}                            

       # Write out compressed dataset
       # ---------------------------- 
       if verbose:
           print('[] Writing',filename)
       self.to_netcdf(filename,engine='netcdf4',format='NETCDF4',encoding=encode)     

    def 
       
#----
       
def wind_direction(u, v):
    """
    Calculates the wind direction in degrees from u and v components.
    This version works with numpy arrays or xarray DataArrays.
    """
    # Ensure u and v are numpy arrays
    u = np.asarray(u)
    v = np.asarray(v)

    # Avoid division by zero issues and compute wind ratio u/v
    windratio = np.where(v > 0.0001, u / v, np.where(u > 0.0001, u * 99999.0, 0.0))

    # Calculate the absolute wind angle (arctangent of the wind ratio)
    windangle = np.arctan(np.abs(windratio))

    # Determine the quadrant based on u and v components
    iquadrant = np.zeros_like(u, dtype=int)

    iquadrant[(u >= 0) & (v >= 0)] = 1
    iquadrant[(u >= 0) & (v < 0)] = 2
    iquadrant[(u < 0) & (v < 0)] = 3
    iquadrant[(u < 0) & (v >= 0)] = 4

    # Quadrant coefficients
    quadcof1 = np.array([0.0, 1.0, 1.0, 2.0])
    quadcof2 = np.array([1.0, -1.0, 1.0, -1.0])

    # Calculate the wind direction in radians
    direction_rad = quadcof1[iquadrant - 1] * np.pi + windangle * quadcof2[iquadrant - 1]

    # Convert radians to degrees
    direction_deg = np.degrees(direction_rad)

    # Normalize the direction to be in the range [0, 360]
    direction_deg = np.where(direction_deg < 0, direction_deg + 360, direction_deg)

    return direction_deg

 
