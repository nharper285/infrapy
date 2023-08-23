from obspy import UTCDateTime
from obspy import read_inventory
from obspy.signal import PPSD
from obspy.clients.fdsn import Client

from datetime import datetime
from statistics import mean
import numpy
import matplotlib.pyplot as plt

# Events
# Rainier
# 5/8/23 13:11:30 13:13:30 - PR04/PR05/STYX/GTWY/TAVI/KAUT/PARA/RER - Wes says one of best events
# 4/20/23 5:36:00-5:38:30 - on PARA/KAUT/GTWY/TAVI/RER/SIFT/PR05/PR04/PR03(?) - Wes says good start, no location shift
# 4/8/23 4:27-4:36 - PARA/KAUT/TAVI/RER - Wes says probable avalanche at miildred
# 1/26/23 8:09:30- 8:11:30 - PARA/OPCH(weak)/KAUT/GTWY/TAVI/RER/MILD/ARAT(?)/SIFT - Wes says big
# 1/16/23 0:23:30-0:31:00 - RER/TAVI/KAUT/COPP/ARAT/MILD/PARA/OPCH(?) - avalanche sweep, may be tricky with BISL

# 8-15
year = 2023
month = 8
day = 15
start_hour = 23
start_minute = 20 
start_second = 0
end_hour = 23
end_minute = 40 
end_second = 0

date = f"{month}-{day}-{year}"

# # 5-8
# year = 2023
# month = 5
# day = 8
# start_hour = 13
# start_minute = 5 
# start_second = 30
# end_hour = 13
# end_minute = 20 
# end_second = 30

# year = 2023
# month = 1
# day = 26
# start_hour = 8
# start_minute = 9 
# start_second = 30
# end_hour = 8
# end_minute = 11 
# end_second = 30

network = "CC"
station = "STYX"
location = "01"
channel = "BDF"

station_list = ["TAVI","ARAT","COPP"] # RER
# station_list = ["PARA", "OPCH", "KAUT", "GTWY", "TAVI", "MILD", "ARAT", "SIFT"]
# station_list = ["PR04","PR05","STYX","GTWY","TAVI","KAUT","PARA"]
# station_list = ["PR04", "PR05", "STYX"]
lat_long_list = []

client = Client('IRIS') 

for station in station_list:
    station_inv = client.get_stations(network=network, station=station, channel=channel, level="response")   
    print(station_inv)
    channels = station_inv.get_contents()['channels']
    print(channels)
    coordinate_list = []
    for channel in channels:
        local = station_inv.get_coordinates(f"{channel}")
        coordinate = [local['latitude'], local['longitude']]
        if coordinate not in coordinate_list:
            coordinate_list.append(coordinate)
        # lat_long_list.append([coordinate['latitude'], coordinate['longitude']])
        fdsn = channel.split(".")
        print(fdsn)
        print(coordinate)
        network, station, location, channel = fdsn[0], fdsn[1], fdsn[2], fdsn[3]
        # print(f"DATE: {UTCDateTime(year, month, day, start_hour, start_minute, start_second, 935000)}")

        try: 
            stream = client.get_waveforms(network, station, location, channel, UTCDateTime(year, month, day, start_hour, start_minute, start_second, 0), UTCDateTime(year, month, day, end_hour, end_minute, end_second, 0), attach_response=True)
            # print(stream)
            # stream.plot()
            stream.write(f'../examples/{date}/{station}/{network}.{station}.{location}.{channel}.SAC', format='SAC')
        except: 
            print(f"FAILED TO RETRIEVE DATA: {UTCDateTime(year, month, day, 0, 0, 0, 935000)}")  
    print(coordinate_list)
    # numpy.save(f"../examples/{station}.npy", coordinate_list)

# local_latlon = numpy.save("local.npy", lat_long_list)

