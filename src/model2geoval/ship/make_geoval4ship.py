from generate_ship_geovals import generate_ship_geovals

# List of satellite sensors
sensor_list  = ['sfcship']

# Date for the data conversion
year = 2019
month = 8
day = 1
analtime = '03'
analtimep3 = '06'

# Loop over each sensor to process data
for sensor in sensor_list:
    generate_ship_geovals(sensor, year, month, day, analtime, analtimep3)

