import numpy as np
import xarray as xr
import datetime
from datetime import timedelta
import math
from scipy import constants


def generate_radiance_geovals(sensor, year, month, day, analtime):
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

    # Print input and output filenames
    print(f"Input file: {infilename}")
    print(f"Output file: {outfilename}")


#========================================================================
# 1. Use xarray to read the NR netCDF file
    try:
       nr_ds = xr.open_dataset(infilename)
    except FileNotFoundError:
       print(f"Error: The file {infilename} does not exist.")
       return

    # List of variables to read from the dataset
    variables = ['latitude', 'longitude', 'dateTime', 'COSZ', 'phis', 'ts', 'frland', 'frlandice', \
                 'frseaice', 'frlake', 'frocean', 'ps', 'U10M', 'V10M', 'T2M', 'Q2M', 'TSOIL1',  \
                 'SNOWDP', 'GWETTOP', 'delp', 'u', 'v', 'tv', 'sphu', 'ozone'] 


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

    # Read NCEP GFS surface file (info:2023-09-01 file)
    sfcfilename = '/discover/nobackup/projects/gmao/nwposse/mkim1/AIST-NR/jedi-ncep-sfc-files/GEOSadas-5.29.5/geos.crtmsrf.c12.nc4'
    try:
      dsfc = xr.open_dataset(sfcfilename)
    except FileNotFoundError:
      print(f"Error: The file {sfcfilename} does not exist.")
      return

    # Extract the surface data variables
    sfclat = dsfc['lats'].values
    sfclon = dsfc['lons'].values
    vtype = dsfc['vtype'].values  # 0 - 20
    stype = dsfc['stype'].values  # 0 - 16
    vfrac = dsfc['vfrac'].values  # 0.0 - 1.0
  
    # Debugging output for checking the shapes of surface variables
    print(f"Surface file variables extracted:")
    print(f"sfclat shape: {sfclat.shape}, sfclon shape: {sfclon.shape}")
    print(f"vtype shape: {vtype.shape}, stype shape: {stype.shape}")
    print(f"vfrac shape: {vfrac.shape}")

    # Close the surface dataset after reading
    dsfc.close()

# 2. 
    # Rearranging NCEP GFS vtype, vfrac, stype to find the nearest point to GEOS NR lat/lon
    # Extract the dimensions of the surface data
    nlocdim1 = sfclat.shape[1]  # Number of latitude grid points
    nlocdim2 = vtype.shape[1]  # Number of surface types (6)

    # Lists to hold the rearranged data
    point_list = []
    vtype_point_list = []
    stype_point_list = []
    vfrac_point_list = []

    # Loop through the surface data to build lists
    for i in range(nlocdim1):
        for j in range(nlocdim1):
            for k in range(nlocdim2):
                point_list.append((sfclat[k, i, j], sfclon[k, i, j]))
                vtype_point_list.append((sfclat[k, i, j], sfclon[k, i, j], vtype[0, k, i, j]))
                vfrac_point_list.append((sfclat[k, i, j], sfclon[k, i, j], vfrac[0, k, i, j]))
                stype_point_list.append((sfclat[k, i, j], sfclon[k, i, j], stype[0, k, i, j]))

    # Convert point list data into numpy arrays for further processing
    vtype_point_array = np.array(vtype_point_list)
    stype_point_array = np.array(stype_point_list)
    vfrac_point_array = np.array(vfrac_point_list)

    # Debugging output for checking the shape of the point arrays
    print(f"Shape of vtype_point_array: {vtype_point_array.shape}")
    print(f"Shape of stype_point_array: {stype_point_array.shape}")
    print(f"Shape of vfrac_point_array: {vfrac_point_array.shape}")


# 3. 
    # Create NR jedi-geovals of which each variables will be filled with values later.
    nlevs= nr_ds.sphu.shape[0]
    nlevsp1 = nlevs+1

    geoval_ds = xr.Dataset()

    # Coordinates
    geoval_ds.coords['nlocs'] = np.arange(nlocs)
    geoval_ds.coords['nlevs'] = np.arange(nlevs)
    geoval_ds.coords['nlevsp1'] = np.arange(nlevsp1)

    #Initialize the latitude and longitude as empty arrays or with dummy values
    geoval_ds['latitude'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['longitude'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    
    # Initialize the time variable as empty or with dummy values
    geoval_ds['time'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    
    # Initialize all other variables as empty arrays with appropriate dimensions
    geoval_ds['water_area_fraction'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['land_area_fraction'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['ice_area_fraction'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_snow_area_fraction'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_temperature_where_sea'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_temperature_where_land'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_temperature_where_ice'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_temperature_where_snow'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['skin_temperature_at_surface_where_sea'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['skin_temperature_at_surface_where_land'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['skin_temperature_at_surface_where_ice'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['skin_temperature_at_surface_where_snow'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['skin_temperature_at_surface'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])

    geoval_ds['soil_temperature'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['volume_fraction_of_condensed_water_in_soil'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['land_type_index_NPOESS'] = xr.DataArray(np.zeros(nlocs, dtype=int), dims=['nlocs'])
    geoval_ds['average_surface_temperature_within_field_of_view'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['vegetation_area_fraction'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_snow_thickness'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_wind_speed'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['wind_speed_at_surface'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['wind_from_direction_at_surface'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['tropopause_pressure'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['vegetation_type_index'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['leaf_area_index'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['soil_type'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_wind_from_direction'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_geopotential_height'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['surface_geometric_height'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['height_above_mean_sea_level_at_surface'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['cloud_volume_fraction_in_atmosphere_layer'] = xr.DataArray(np.zeros(nlocs), dims=['nlocs'])
    geoval_ds['air_temperature_at_two_meters_above_surface'] = xr.DataArray(np.zeros((nlocs)), dims=['nlocs'])
    geoval_ds['water_vapor_mixing_ratio_wrt_moist_air_at_2m'] = xr.DataArray(np.zeros((nlocs)), dims=['nlocs'])
    
    # For 2D variables (e.g., air_temperature, air_pressure, humidity_mixing_ratio), we need to specify both nlocs and nlevs/nlevsp1
    geoval_ds['air_temperature'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['air_pressure'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['air_pressure_levels'] = xr.DataArray(np.zeros((nlocs, nlevsp1)), dims=['nlocs', 'nlevsp1'])
    geoval_ds['humidity_mixing_ratio'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['water_vapor_mixing_ratio_wrt_dry_air'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['mole_fraction_of_ozone_in_air'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    geoval_ds['mole_fraction_of_carbon_dioxide_in_air'] = xr.DataArray(np.zeros((nlocs, nlevs)), dims=['nlocs', 'nlevs'])
    
    # Now geoval_ds is initialized with empty arrays, and you can fill the variables as needed.
    # For example, you can assign data to geoval_ds['surface_temperature_where_sea'] later
    # geoval_ds['surface_temperature_where_sea'][:] = new_values_for_surface_temperature
    
    # Optional: Save to NetCDF file
    # geoval_ds.to_netcdf(outfilename, format='NETCDF4')
    
    # Inspect the resulting dataset (optional)
    print(geoval_ds)
    
#4
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
#5
    ### Surface Type Area Fraction ###
    # ---------------------------
    # Initialize surface area fractions
    geoval_ds['water_area_fraction'][:] = nr_ds['frocean'].values + nr_ds['frlake'].values
    geoval_ds['land_area_fraction'][:] = nr_ds['frland'].values
    geoval_ds['ice_area_fraction'][:] = nr_ds['frseaice'].values + nr_ds['frlandice'].values
    geoval_ds['cloud_volume_fraction_in_atmosphere_layer'] = 0.0
 

    # Adjust water_area_fraction where sea ice exists
    for i in range(nlocs):
        if nr_ds['frseaice'][i] > 0.0 and geoval_ds['water_area_fraction'][i] > 0.0:
            geoval_ds['water_area_fraction'][i] -= nr_ds['frseaice'][i]  # Subtract the ice fraction from the water fraction

    # Initialize surface snow area fraction
    geoval_ds['surface_snow_area_fraction'][:] = 0.0

    # Calculate total area fraction for each location
    tot_frac = np.copy(geoval_ds['water_area_fraction'].values)

    # Loop to adjust surface snow and land/ice fractions where snow depth is non-zero
    for i in range(nlocs):
        if nr_ds['SNOWDP'][i] > 0.0001 and nr_ds['SNOWDP'][i] < 1000000.:
            geoval_ds['surface_snow_area_fraction'][i] = geoval_ds['ice_area_fraction'][i] + geoval_ds['land_area_fraction'][i]
            geoval_ds['ice_area_fraction'][i] = 0.0  # Snow takes over ice
            geoval_ds['land_area_fraction'][i] = 0.0  # Snow takes over land

        # Update the total fraction for each location
        tot_frac[i] = geoval_ds['water_area_fraction'][i] + geoval_ds['land_area_fraction'][i] \
                    + geoval_ds['surface_snow_area_fraction'][i] + geoval_ds['ice_area_fraction'][i]

    # Debugging output for total area fractions
    print('Total area fraction min:max = ', np.min(tot_frac), np.max(tot_frac))

    # Final Adjustments ###
    # Ensure total area fractions sum to 1 at each location (or very close to 1)
    for i in range(nlocs):
        if np.abs(tot_frac[i] - 1) > 1e-3:
            print(f"Warning: Total area fraction for location {i} is {tot_frac[i]} (expected 1).")

    ### Surface tempeature 
    # ---------------------------
    geoval_ds['surface_temperature_where_sea'][:]  = nr_ds['ts'][:]
    geoval_ds['skin_temperature_at_surface_where_sea'][:]  = nr_ds['ts'][:]
    geoval_ds['surface_temperature_where_land'][:] = nr_ds['ts'][:]
    geoval_ds['skin_temperature_at_surface_where_land'][:]  = nr_ds['ts'][:]
    geoval_ds['surface_temperature_where_ice'][:]  = nr_ds['ts'][:]
    geoval_ds['skin_temperature_at_surface_where_ice'][:]  = nr_ds['ts'][:]
    geoval_ds['surface_temperature_where_snow'][:] = nr_ds['ts'][:]
    geoval_ds['skin_temperature_at_surface_where_snow'][:]  = nr_ds['ts'][:]
    geoval_ds['skin_temperature_at_surface'][:]  = nr_ds['ts'][:]
    geoval_ds['air_temperature_at_two_meters_above_surface'] = nr_ds['T2M'] 
    geoval_ds['water_vapor_mixing_ratio_wrt_moist_air_at_2m'] = nr_ds['Q2M'] 

    ### Surface wind speed and direction 
    # ---------------------------
    u10 = nr_ds['U10M'].values  # Shape should be (nlocs,)
    v10 = nr_ds['V10M'].values  # Shape should be (nlocs,)

    # Compute surface wind speed (element-wise)
    surface_wind_speed = np.sqrt(np.maximum(u10**2 + v10**2, 0.9e-4))

    # Compute wind direction for locations where wind speed is above a threshold
    surface_wind_from_direction = np.zeros_like(surface_wind_speed)

    # Mask for wind speeds greater than the threshold
    mask = surface_wind_speed > 0.001

    # Apply the wind direction calculation only to the masked locations
    surface_wind_from_direction[mask] = wind_direction(u10[mask], v10[mask])

    # Normalize wind direction to be within 0-360 degrees
    surface_wind_from_direction[surface_wind_from_direction < 0] += 360.0

    # Store the results into geoval_ds (or wherever necessary)
    geoval_ds['surface_wind_speed'][:] = surface_wind_speed
    geoval_ds['surface_wind_from_direction'][:] = surface_wind_from_direction

    geoval_ds['wind_speed_at_surface'][:] = surface_wind_speed
    geoval_ds['wind_from_direction_at_surface'][:] =  surface_wind_from_direction


    ### Soil and veg types
    # ---------------------------
    # Define necessary lookup lists and constants
    igbp_n_types = 20  # Number of vegetation types
    igbp_to_gfs = [4, 1, 5, 2, 3, 8, 9, 6, 6, 7, 8, 12, 7, 12, 13, 11, 0, 10, 10, 11]
    map_soil_to_crtm = [1, 1, 4, 2, 2, 8, 7, 2, 6, 5, 2, 3, 8, 1, 6, 9]

    # Precompute point list indices for faster lookup
    point_list_dict = {tuple(point): idx for idx, point in enumerate(point_list)}  # Assuming point_list contains tuples (lat, lon)

    # Initialize necessary arrays
    land_type_index_NPOESS = np.zeros(nlocs)
    soil_type = np.zeros(nlocs)
    vegetation_type_index = np.zeros(nlocs)
    vegetation_area_fraction = np.zeros(nlocs)
    leaf_area_index = np.zeros(nlocs)

    # Convert 'latitude' and 'longitude' to a tuple of (lat, lon) to directly access the index from the point list
    latitudes = nr_ds['latitude'].values
    longitudes = nr_ds['longitude'].values

    # Loop over each location
    for i in range(nlocs):
       target_point = (latitudes[i], longitudes[i])
       nearest_point_idx = find_nearest_point(target_point, point_list)

       land_type_index_NPOESS[i] = stype_point_array[point_list.index(nearest_point_idx)][2]
       soil_type[i] = stype_point_array[point_list.index(nearest_point_idx)][2]
       vegetation_type_index[i] = vtype_point_array[point_list.index(nearest_point_idx)][2]
       vegetation_area_fraction[i] = vfrac_point_array[point_list.index(nearest_point_idx)][2]

       vegetation_type_index[i] = max(1.0, min(vegetation_type_index[i], 20.0))
       soil_type[i] = max(1.0, min(soil_type[i], 16.0))

       # Apply the mapping to vegetation and soil type indices
       vegetation_type_index[i] = igbp_to_gfs[int(vegetation_type_index[i])-1]
       land_type_index_NPOESS[i] = igbp_to_gfs[int(vegetation_type_index[i])-1] 
       soil_type[i] = map_soil_to_crtm[int(soil_type[i])-1] 

       # Compute leaf area index (LAI) using day_of_year_value and vegetation type
       lai = get_lai(day_of_year_value, latitudes[i], int(vegetation_type_index[i]))
       leaf_area_index[i] = lai

    # Fill geoval_ds with the computed values
    geoval_ds['land_type_index_NPOESS'][:] = land_type_index_NPOESS[:]
    geoval_ds['soil_type'][:] = soil_type[:]
    geoval_ds['vegetation_type_index'][:] = vegetation_type_index[:]
    geoval_ds['vegetation_area_fraction'][:] = vegetation_area_fraction[:]
    geoval_ds['leaf_area_index'][:] = leaf_area_index[:]


    # Other land surface related variables from GEOS NR
    #---------------------------------------------------

    # Assign arrays directly from `nr_ds`
    geoval_ds['soil_temperature'][:] = nr_ds['TSOIL1'][:]
    geoval_ds['volume_fraction_of_condensed_water_in_soil'][:] = nr_ds['GWETTOP'][:]  # Check unit
    geoval_ds['average_surface_temperature_within_field_of_view'][:] = nr_ds['ts'][:]  # Temporary
    geoval_ds['surface_snow_thickness'][:] = nr_ds['SNOWDP'][:]  # Check unit

    # Tropopause info
    #---------------------------------------------------
    # Temporary values for tropopause pressure (adjust as needed)
    geoval_ds['tropopause_pressure'][:] = 20000.  # Temporary. Not used in CRTM? 
    # Geopotential height conversion
    geoval_ds['surface_geopotential_height'][:] = nr_ds['phis'][:] / constants.g  # phis[m2 sec-2] --> geo.pot.height[m]
    geoval_ds['surface_geometric_height'][:] = geoval_ds['surface_geopotential_height'][:] * 6371000.0 / (6371000.0 - geoval_ds['surface_geopotential_height'][:])
    geoval_ds['height_above_mean_sea_level_at_surface'][:] = geoval_ds['surface_geopotential_height'][:] * 6371000.0 / (6371000.0 - geoval_ds['surface_geopotential_height'][:])
  
    # Atmospheric profile info
    #---------------------------------------------------
    # Air temperature calculation (vectorized for all locations)
    geoval_ds['air_temperature'][:] = (nr_ds['tv'][:] / (1.0 + 0.60773 * nr_ds['sphu'][:])).T
    
    # Humidity mixing ratio calculation (vectorized for all locations)
    geoval_ds['humidity_mixing_ratio'][:] = 1000.0 * nr_ds['sphu'][:].T / (1.0 - nr_ds['sphu'][:].T)
    geoval_ds['water_vapor_mixing_ratio_wrt_dry_air'][:] = 1000.0 * nr_ds['sphu'][:].T / (1.0 - nr_ds['sphu'][:].T)
     
    # Temporary values for ozone and CO2 mole fractions (adjust as needed)
    geoval_ds['mole_fraction_of_ozone_in_air'][:] = 0.02  # Temporary value
    geoval_ds['mole_fraction_of_carbon_dioxide_in_air'][:] = 410.0  # Temporary value


    # Initialize the first pressure level (top of atmosphere) at 0.5 Pa
    geoval_ds['air_pressure_levels'][:, 0] = 0.5  # Unit: Pa 
    cumulative_delp = np.cumsum(np.vstack([np.zeros((1, nlocs)), nr_ds['delp']]), axis=0)
    geoval_ds['air_pressure_levels'][:,:] = cumulative_delp[:,:].T + geoval_ds['air_pressure_levels'][:, 0:1].values
    geoval_ds['air_pressure_levels'][:,nlevsp1-1] = nr_ds['ps'][:]  # Unit: Pa

    p1=geoval_ds['air_pressure_levels'][:,0:nlevsp1-1]
    p2=geoval_ds['air_pressure_levels'][:,1:nlevsp1]
    print(geoval_ds['air_pressure'].shape)
    print(p1.shape)
    print(p2.shape)
    for k in range(nlevs):
        geoval_ds['air_pressure'][:, k] = (geoval_ds['air_pressure_levels'][:, k] + geoval_ds['air_pressure_levels'][:, k + 1]) * 0.5  


#Finally,
    # Save the new dataset to a new jedi geoval file
    print(f"Saving the new JEDI geoval file to {outfilename}") 
    geoval_ds.to_netcdf(outfilename)


#========================================================================
# Finds the nearest point in the list to the target point.
def find_nearest_point(target_point, point_list):
      """
      Args:
          target_point: A tuple representing the (x, y) coordinates of the target point.
          point_list: A list of tuples representing the (x, y) coordinates of points.
          
      Returns: 
          A tuple representing the (x, y) coordinates of the nearest point.
      """
          
      nearest_point = None
      min_distance = float('inf')

      for point in point_list:
          distance = math.sqrt((point[0] - target_point[0])**2 + (point[1] - target_point[1])**2)
          if distance < min_distance:
              min_distance = distance
              nearest_point = point
            
      return nearest_point
       
#========================================================================
# Compute  Leaf-area Index 
def get_lai(rjday, lat, ivegtype):
      dayhf = [15.5, 196.5, 380.5]
      lai_min = [3.08 , 1.85 , 2.80 , 5.00 , 1.00 ,
                 0.50 , 0.52 , 0.60 , 0.50 , 0.60 ,
                 0.10 , 1.56 , 0.01   ]
      lai_max = [6.48 , 3.31 , 5.50 , 6.40 , 5.16 ,
                 3.66 , 2.90 , 2.60 , 3.66 , 2.60 ,
                 0.75 , 5.68 , 0.01   ]
      lai_season = [0.0, 0.0]
      for mm in range(3):
        mmm = mm
        mmp = mm + 1
        if rjday > dayhf[mmm] and rjday < dayhf[mmp] :
           n1 = mmm
           n2 = mmp
           exit
      wei1s = (dayhf[n2] - rjday) / (dayhf[n2] - dayhf[n1])
      wei2s = (rjday - dayhf[n1]) / (dayhf[n2] - dayhf[n1])

      lai_season[0] = lai_min[ivegtype-1]
      lai_season[1] = lai_max[ivegtype-1]

      if lat < 0.0 :
        lai = wei1s * lai_season[n2-1] + wei2s * lai_season[n1-1]
      else:
        lai = wei1s * lai_season[n1-1] + wei2s * lai_season[n2-1]

      return lai

#========================================================================
# Compute  day of the year (for get_lai) 
def day_of_year(year, month, day):
     """Calculates the day of the year for a given date."""
     date = datetime.date(year, month, day)
     return date.timetuple().tm_yday

#========================================================================
# Compute wind direction 
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

