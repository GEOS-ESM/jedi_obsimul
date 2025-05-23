from generate_satwind_geovals import generate_satwind_geovals

# List of satellite sensors
sensor_list  = ['satwind']

# Date for the data conversion
year = 2019
month = 8
day = 1
analtime = '03'
analtimep3 = '06'

# Loop over each sensor to process data
for sensor in sensor_list:
    generate_satwind_geovals(sensor, year, month, day, analtime, analtimep3)

