#!/usr/bin/env python  -W ignore::DeprecationWarning

# test_detection.py
#
# Tutorial for detection utilizing the AFD on a series of beamforming results, saved in a file as
#
# @fkdd (fransiska at lanl dot gov)
# @pblom (pblom at lanl dot gov)
# Last Modified 12/19/2019

import numpy as np
import json
import pathos.multiprocessing as mp
from multiprocessing import cpu_count

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from obspy.core import read

from scipy import signal

from infrapy.detection import beamforming_new
from infrapy.utils import data_io

# ######################### #
#     Define Parameters     #
# ######################### #

# Detection params
# times_file, beam_results_file = None, None
times_file, beam_results_file = "KAUT/times.npy", "KAUT/beam_results.npy"

det_win_len = 60 * 5
det_thresh = 0.50
min_seq = 5
TB_prod = 40 * 10
back_az_lim = 10
channel_cnt = 3

freq_min = 1.0
freq_max = 5.0

sig_start, sig_end = 0, 850

sac_glob = "KAUT/*.SAC"
# lat_lon = [[46.740208, -121.916966], [46.740163, -121.916765], [46.740088, -121.916968]] # GTW_Y_
lat_lon = [[46.963808, -122.08058], [46.963597, -122.080718], [46.963646, -122.080262]] # KAU_T_
# lat_lon = [[46.78665, -121.74226], [46.786445, -121.74189], [46.786401, -121.742169]] # PAR_A_
# lat_lon = [[46.92976, -121.98847], [46.92982, -121.98924], [46.93017, -121.98831]] # PR0_4_
# lat_lon = [[46.84195, -121.94906], [46.8417, -121.9487], [46.8418, -121.948967]] # PR0_5_
# lat_lon = [[46.963808, -122.08058], [46.963597, -122.080718], [46.963646, -122.080262]] # STY_X_
# lat_lon = [[46.740208, -121.916966], [46.730263, -121.857381], [46.786441, -121.742195], [46.929773, -121.988592], [46.841723, -121.948863], [46.963747, -122.080535], [46.7957, -121.88423]]
    
if __name__ == '__main__':
    ######################################
    ##  Load data and prepare analysis  ##
    ######################################

    if times_file and beam_results_file:
        times = np.load(times_file)
        beam_results = np.load(beam_results_file)
        # print(beam_results)
        # print(times)
    else:
        print('No beamforming input provided')

    ######################################
    ##      Run detection analysis      ##
    ######################################
    #detect_signals(times, beam_results, win_len, TB_prod, channel_cnt, det_p_val=0.99, min_seq=5, back_az_lim=15, fixed_thresh=None, return_thresh=False)

    dets = beamforming_new.detect_signals(times, beam_results, det_win_len, TB_prod, channel_cnt, min_seq=min_seq, back_az_lim=back_az_lim)

    print('\n' + "Detection Summary:")
    dets_list = []
    for det in dets:
        print("Detection time:", det[0], '\t', "Rel. detection onset:", det[1], '\t',"Rel. detection end:", det[2], '\t',end=' ')
        print("Back azimuth:", np.round(det[3], 2), '\t', "Trace velocity:", np.round(det[4], 2), '\t', "F-stat:", np.round(det[5], 2), '\t', "Array dim:", channel_cnt)
        dets_dict = {
            "Name":"", 
            "Time (UTC)": f"{det[0]}",
            "F Stat.": det[5],
            "Trace Vel. (m/s)": det[4],
            "Back Azimuth": det[3],
            "Latitude": lat_lon[0][0],
            "Longitude":  lat_lon[0][1],
            "Elevation (m)": "",
            "Start": "",
            "End": "",
            "Freq Range": "",
            "Array Dim.":  3,
            "Method": "",
            "Event": "",
            "Note": ""
            }
        dets_list.append(dets_dict)
    with open(".\KAUT\\results.dets.json", "w") as outfile:
        json.dump(dets_list, outfile)
    plt.figure()

plt.suptitle("Detection results for analysis \n Filtered in frequency range: " + str(freq_min) + " - " + str(freq_max) + "  Hz \n ")

x, t, t0, geom = beamforming_new.stream_to_array_data(read(sac_glob), latlon=lat_lon)
M, N = x.shape

for det in range(len(dets)):
    dt = dets[det][0]-times[0] 
    start = dt.item().total_seconds() 
    ts = sig_start + start + dets[det][1]
    te = sig_start + start + dets[det][2]
    for m in range(M):
        plt.subplot(M, 1, m + 1)
        plt.xlim([sig_start, sig_end])
        plt.plot(t, x[m], 'k-')
        plt.axvspan(xmin = ts , xmax = te, alpha = 0.25, color = 'blue')
        if m < (M - 1) : plt.setp(plt.subplot(M, 1, m + 1).get_xticklabels(), visible=False)
    
plt.show()

# det_list = []
#     for det_info in dets:
#         det_list = det_list + [data_io.define_detection(det_info, [array_lat, array_lon], channel_cnt, [freq_min,freq_max], note="InfraPy CLI detection", method=method)]
#     print("Writing detections to " + local_detect_label + ".dets.json")
#     data_io.detection_list_to_json(local_detect_label + ".dets.json", det_list, stream_info)