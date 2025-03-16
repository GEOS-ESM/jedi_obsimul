from generate_radiance_geovals import generate_radiance_geovals

# List of satellite sensors
sensor_list  = [
          'airs_aqua','amsr2_gcom-w1','amsua_aqua','amsua_metop-b','amsua_n15','amsua_n18','amsua_n19','atms_n20','atms_npp',
          'avhrr3_metop-b','avhrr3_n18','avhrr3_n19','cris-fsr_n20','cris_fsr_npp','gmi_gpm','gps','iasi_metop-b',
          'mhs_metop-b','mhs_n19','ssmis_f17'
]

# Date for the data conversion
year = 2019
month = 8
day = 1
analtime = '03'

# Loop over each sensor to process data
for sensor in sensor_list:
    generate_radiance_geovals(sensor, year, month, day, analtime)

