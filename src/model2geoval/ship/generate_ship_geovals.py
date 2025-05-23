import numpy as np
import xarray as xr
import datetime
from datetime import timedelta
import math
from scipy import constants


def generate_ship_geovals(sensor, year, month, day, analtime, analtimep3):
    """
    Function to generate radiance geovals for a given sensor and date.

    Parameters:
    - sensor (str): The sensor identifier.
    - year (int): Year of the data.
    - month (int): Month of the data.
    - day (int): Day of the data.
    - analtime (str): Analysis time (e.g., '03').
    """
    print(f"Processing {sensor} for {year}-{month:02d}-{day:02d} at {analtime}Z")

    # Construct paths for input and output files
    month_str = str(month).zfill(2)
    day_str = str(day).zfill(2)

    # Directory and filename for input and output data
    nrdirectory = '/discover/nobackup/projects/gmao/aist-nr/yyu11/run_geos_su17/c180_L137_test_sampler/scratch.jedi.works/'
    infilename = f"{nrdirectory}{sensor}.AIST_c180_L137.jedi.{year}{month_str}{day_str}_{analtime}00z.nc4"
    outfilename = f"{sensor}_geovals.{year}{month_str}{day_str}T{analtime}0000Z.nc4"
    iodadirectory = f"/discover/nobackup/projects/gmao/aist-nr/data/ioda/{year}{month_str}{day_str}T{analtimep3}0000Z/geos_atmosphere/"
    iodafilename = f"{iodadirectory}{sensor}.{year}{month_str}{day_str}T{analtime}0000Z.nc4"

    # Print input and output filenames
    print(f"Input file: {infilename}")
    print(f"Output file: {outfilename}")
    print(f"IODA file: {iodafilename}")

#========================================================================
# 1a. Use xarray to read the NR netCDF file
    # ---------------------------
    try:
       nr_ds = xr.open_dataset(infilename)
    except FileNotFoundError:
       print(f"Error: The file {infilename} does not exist.")
       return

    # List of variables to read from the dataset
    variables = ['latitude', 'longitude', 'dateTime', 'COSZ', 'phis', 'ts', 'frland', 'frlandice', \
                 'frseaice', 'frlake', 'frocean', 'ps', 'U10M', 'V10M', 'T2M', 'Q2M', 'TSOIL1',  \
                 'SNOWDP', 'GWETTOP', 'delp', 'u', 'v', 'tv', 'sphu', 'ozone','Z0M'] 


    # Extract variables from the dataset
    data = {var: nr_ds[var].values for var in variables}
 
  
    # Extract the latitude shape to determine the number of locations
    nlocs = data['latitude'].shape[0]


    # Debugging output for checking the shapes
    print(f"Number of obs locations: {nlocs}")
    print(f"Shape of latitude: {data['latitude'].shape}")  
    print(f"Shape of longitude: {data['longitude'].shape}")  
    
    for var, values in data.items():
       print(f"{var}: {values.shape}")
  

    # Close the dataset after processing
    nr_ds.close()

# 1b. Read the sample ioda file 
    # ---------------------------
    try:
       ioda_ds = xr.open_dataset(iodafilename, group='MetaData')
    except FileNotFoundError:
       print(f"Error: The file {iodafilename} does not exist.")
       return
    ioda_lat = ioda_ds['latitude'].values
    ioda_lon = ioda_ds['longitude'].values
    ioda_satidentifier = ioda_ds['satelliteIdentifier'].values

# 2. 
    # Create NR jedi-geovals of which each variables will be filled with values later.
    nlevs= nr_ds.sphu.shape[0]
    ninterfaces = nlevs + 1

    geoval_ds = xr.Dataset()

    # Coordinates
    geoval_ds.coords['nlocs'] = np.arange(nlocs)
    geoval_ds.coords['nlevs'] = np.arange(nlevs)
    geoval_ds.coords['ninterfaces'] = np.arange(ninterfaces)
    
    # Initialize variables
    geoval_ds['latitude'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['longitude'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['time'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    
    geoval_ds['land_area_fraction'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_geometric_height'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_geopotential_height'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_pressure'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_roughness'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_temperature'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_saturation_specific_humidity'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['wind_reduction_factor_at_10m'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['tropopause_pressure'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    
    # For 2D variables (e.g., air_temperature, air_pressure), we need to specify both nlocs and nlevs/ninterfaces
    geoval_ds['air_pressure'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['air_temperature'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['dup_kx_vector'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['eastward_wind'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['geopotential_height'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['northward_wind'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['specific_humidity'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['virtual_temperature'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['saturation_specific_humidity'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['geometric_height'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
   
    geoval_ds['air_pressure_levels'] = xr.DataArray(np.zeros((nlocs, ninterfaces)), dims=['nlocs', 'ninterfaces'])
     
#3
    # Fill in the 'latitude' and 'longitude' values from NR dataset
    # ---------------------------
    geoval_ds['latitude'][:] = nr_ds['latitude'].values[:geoval_ds.dims['nlocs']]
    geoval_ds['longitude'][:] = nr_ds['longitude'].values[:geoval_ds.dims['nlocs']]

    # Time Variables ###
    # ---------------------------
    yy = year
    mm = month
    dd = day
    hh = int(analtime)

    # Convert analysis_time to total seconds since the Unix epoch
    analysis_time = datetime.datetime(yy,mm,dd,hh) - datetime.datetime(1970,1,1) + timedelta(hours=3)
    analysis_time_seconds = analysis_time.total_seconds()

    # Convert nr_ds['dateTime'] (datetime64[ns]) to total seconds since the Unix epoch
    dateTime_seconds = (nr_ds['dateTime'].values - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')

    # Calculate the time difference in hours
    geoval_ds['time'][:] = (dateTime_seconds - analysis_time_seconds) / 3600  # Convert to hours

    # Calculate the day of the year
    day_of_year_value = day_of_year(yy, mm, dd)
    print("Day of the year:", day_of_year_value)

    # station index info
    #---------------------------
    for i in range(nlocs):
       geoval_ds['dup_kx_vector'][i,:] = ioda_satidentifier[i]

#4  Surface variables
    eps = 0.621837  # eps = rd/rv = 287.04/461.6
    omeps = 0.3781629 # omeps = 1 - eps

    # Surface index  
    geoval_ds['land_area_fraction'][:] = nr_ds['frland'].values

    # Surface wind speed and direction
    # Directly assign the values from u and v to the respective wind variables
    geoval_ds['eastward_wind'][:] = nr_ds['u'].T  # Transpose u so that it matches the correct dimensions (nlocs, nlevs)
    geoval_ds['northward_wind'][:] = nr_ds['v'].T  # Transpose v similarly
     
    # Height info
    # Compute surface_geopotential_height and surface_geometric_height
    geoval_ds['surface_geopotential_height'][:] = nr_ds['phis'] / constants.g
    geoval_ds['surface_geometric_height'][:] = geoval_ds['surface_geopotential_height'] * 6371000.0 \
                                            / (6371000.0 - geoval_ds['surface_geopotential_height'])
     
    # Assign values directly for surface pressure, roughness, and temperature
    geoval_ds['surface_pressure'][:] = nr_ds['ps']
    geoval_ds['surface_roughness'][:] = nr_ds['Z0M']
    geoval_ds['surface_temperature'][:] = nr_ds['T2M']
    geoval_ds['wind_reduction_factor_at_10m'].values[:] = 1.0



    # For surface level saturation vapor pressure and specific humidity
    surface_saturation_vapor_pressure = 0.01 * 611.2 * np.exp( 17.67 * (geoval_ds['surface_temperature'] - 273.15) / 
                                                               (geoval_ds['surface_temperature'] - 273.15 + 243.5))
    geoval_ds['surface_saturation_specific_humidity'][:] = eps * surface_saturation_vapor_pressure \
                       / (geoval_ds['surface_pressure'] - omeps * surface_saturation_vapor_pressure)

#5 2D variables

    # Atmospheric profile info
    #---------------------------------------------------
    # Air temperature calculation (vectorized for all locations)
    geoval_ds['air_temperature'][:] = (nr_ds['tv'][:] / (1.0 + 0.60773 * nr_ds['sphu'][:])).T
    geoval_ds['virtual_temperature'][:] = nr_ds['tv'][:].T
    geoval_ds['specific_humidity'][:] = nr_ds['sphu'][:].T
    
    # Initialize the first pressure level (top of atmosphere) at 0.5 Pa
    geoval_ds['air_pressure_levels'][:, 0] = 0.5  # Unit: Pa 
    cumulative_delp = np.cumsum(np.vstack([np.zeros((1, nlocs)), nr_ds['delp']]), axis=0)
    geoval_ds['air_pressure_levels'][:,:] = cumulative_delp[:,:].T + geoval_ds['air_pressure_levels'][:, 0:1].values
    geoval_ds['air_pressure_levels'][:,ninterfaces-1] = nr_ds['ps'][:]  # Unit: Pa
    for k in range(nlevs):
        geoval_ds['air_pressure'][:, k] = (geoval_ds['air_pressure_levels'][:, k] + geoval_ds['air_pressure_levels'][:, k + 1]) * 0.5

    # Compute the saturation vapor pressure for all levels and locations
    saturation_vapor_pressure = 0.01 * 611.2 * np.exp( 17.67 * (geoval_ds['air_temperature'] - 273.15) / 
                                                       (geoval_ds['air_temperature'] - 273.15 + 243.5))
    # Compute the saturation specific humidity for all levels and locations
    geoval_ds['saturation_specific_humidity'][:] = eps * saturation_vapor_pressure / (geoval_ds['air_pressure'] \
                                                 - omeps * saturation_vapor_pressure)
    # Reverse all the relevant variables 
    geoval_ds['virtual_temperature'].values[:,:] = geoval_ds['virtual_temperature'].values[:,::-1]
    geoval_ds['air_temperature'].values[:,:] = geoval_ds['air_temperature'].values[:,::-1]
    geoval_ds['air_pressure'].values[:,:] = geoval_ds['air_pressure'].values[:,::-1]
    geoval_ds['air_pressure_levels'].values[:,:] = geoval_ds['air_pressure_levels'].values[:,::-1]
    geoval_ds['specific_humidity'].values[:,:] = geoval_ds['specific_humidity'].values[:,::-1]
    geoval_ds['saturation_specific_humidity'].values[:,:] = geoval_ds['saturation_specific_humidity'].values[:,::-1]
    geoval_ds['eastward_wind'].values[:,:] = geoval_ds['eastward_wind'].values[:,::-1]
    geoval_ds['northward_wind'].values[:,:] = geoval_ds['northward_wind'].values[:,::-1]
    print('Done reversing')
    
    ### geopotential height
    virtual_temp = geoval_ds['virtual_temperature'].values
    air_pressure_levels = geoval_ds['air_pressure_levels'].values
    air_pressure = geoval_ds['air_pressure'].values
    geoval_ds['geopotential_height'][:,0] = 29.3 * virtual_temp[:,0] * np.log(air_pressure_levels[:,0] / air_pressure[:,0]) \
                                              + nr_ds['phis'] / constants.g


    for k in range(1,nlevs):
       geoval_ds['geopotential_height'][:, k] = geoval_ds['geopotential_height'][:, k-1] \
                          + 29.3 * virtual_temp[:, k] * np.log(air_pressure[:, k-1] / geoval_ds['air_pressure'][:, k])   
 
#Finally,
    # Save the new dataset to a new jedi geoval file
    print(f"Saving the new JEDI geoval file to {outfilename}") 
    geoval_ds.to_netcdf(outfilename)
#========================================================================
# Compute  day of the year (for get_lai) 
def day_of_year(year, month, day):
     """Calculates the day of the year for a given date."""
     date = datetime.date(year, month, day)
     return date.timetuple().tm_yday

