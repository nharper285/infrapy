from obspy import UTCDateTime 
from obspy.clients.fdsn import Client

import numpy

station_list = ["PR04","PR05","STYX","GTWY","TAVI","KAUT","PARA"]

client = Client('IRIS')

for station in station_list:     
    inv = client.get_stations(network='CC', station=station, location='*', channel='BDF', starttime=UTCDateTime(), level='response')
    coord_list = []
    for i in ["01", "02", "03"]:
        seed = f'CC.{station}.{i}.BDF'
        print("SEED: " + seed)
        coord = inv.get_coordinates(seed_id=seed)
        coord_list.append([coord['latitude'], coord['longitude']])
    print(coord_list)
    numpy.save(f"{station}.npy", coord_list)




# print(inv.get_coordinates(seed_id='CC.PR04.01.BDF')) 
# # Out[12]: 
# # {'latitude': 46.93003,
# #  'longitude': -121.988387,
# #  'elevation': 911.0,
# #  'local_depth': 0.0}
# print(inv.get_coordinates(seed_id='CC.PR04.02.BDF'))
# # Out[13]: 
# # {'latitude': 46.929746,
# #  'longitude': -121.988485,
# #  'elevation': 914.1,
# #  'local_depth': 0.0}
# print(inv.get_coordinates(seed_id='CC.PR04.03.BDF'))
# # Out[14]: 
# # {'latitude': 46.929694,
# #  'longitude': -121.988976,
# #  'elevation': 912.7,
# #  'local_depth': 0.0}
