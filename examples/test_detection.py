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
import re
import os
import sys
import pathos.multiprocessing as mp
from multiprocessing import cpu_count

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from obspy.core import read

from scipy import signal

from infrapy.detection import beamforming_new
from infrapy.detection import visualization as det_vis
from infrapy.utils import data_io

if __name__ == '__main__':
    
    np.set_printoptions(threshold=sys.maxsize)

    # ######################### #
    #     Define Parameters     #
    # ######################### #

    # Detection params
    # times_file, beam_results_file = None, None
    local_detect_label = "COPP"
    date = "8-15-2023"
    ### MUST UPDATE, FLOATS ONLY
    fk_freq_min, fk_freq_max = 5.0, 20.0 
    manual_freq_label = f"{fk_freq_min}_{fk_freq_max}"
    # fk_window_len = 10.0
    # window_step = 2.0
    
    times_file, beam_results_file = f"./{date}/{local_detect_label}/times.npy", f"./{date}/{local_detect_label}/beam_results.npy"
    sac_glob = f"./{date}/{local_detect_label}/*.SAC"
    stream = read(sac_glob)
    lat_lon = np.load(f"./{date}/{local_detect_label}/{local_detect_label}.npy")

    sig_start, sig_end = None, None

   

    det_win_len = 3600
    p_value = 0.05
    min_duration = 20.0
    back_az_width = 15
    fixed_thresh = None
    thresh_ceil = None
    det_thresh = None
    return_thresh = False
    merge_dets = False

    # min_seq = max(2, int(min_duration / fk_window_len))
    # TB_prod = (fk_freq_max - fk_freq_min) * fk_window_len
    # channel_cnt = len(lat_lon)
    ######################################
    ##  Load data and prepare analysis  ##
    ######################################

    # if times_file and beam_results_file:
    #     beam_times = np.load(times_file)
    #     beam_peaks = np.load(beam_results_file)
    # else:
    #     print('No beamforming input provided')

    temp = np.loadtxt(f"./{date}/{local_detect_label}/{local_detect_label}_{manual_freq_label}.fk_results.dat")
    dt, beam_peaks = temp[:, 0], temp[:, 1:]
    print(beam_peaks)
    temp = open(f"./{date}/{local_detect_label}/{local_detect_label}_{manual_freq_label}.fk_results.dat", 'r')
    data_info = []
    for line in temp:
        if "t0:" in line:
            t0 = np.datetime64(line.split(' ')[-1][:-1])
        elif "freq_min" in line:
            file_freq_min = float(line.split(' ')[-1])
        elif "freq_max" in line:
            file_freq_max = float(line.split(' ')[-1])
        elif "window_len" in line and "sub_window_len" not in line:
            fk_window_len = float(line.split(' ')[-1])
        elif "channel_cnt" in line:
            channel_cnt = float(line.split(' ')[-1])
        elif "latitude" in line:
            array_lat = float(line.split(' ')[-1])
        elif "longitude" in line:
            array_lon = float(line.split(' ')[-1])
        elif re.search(r'([\d]{4}-[\d]{2}-[\d]{2})',line) is not None and "t0" not in line:
            data_info.append(line[6:].split('\t')[0])
        elif "method" in line:
            method = line.split(' ')[-1][:-1]

    freq_label = f"{file_freq_min}_{file_freq_max}"
    
    if freq_label != manual_freq_label:
        print(f"{freq_label} {manual_freq_label}")
        print("FREQUENCY LABELS DON'T MATCH. RERUN WITH CORRECT LABELS. EXITING.")
        sys.exit()
    
    beam_times = np.array([t0 + np.timedelta64(int(dt_n * 1e3), 'ms') for dt_n in dt])
    stream_info = [os.path.commonprefix([info.split('.')[j] for info in data_info]) for j in [0,1,3]]

    TB_prod = (file_freq_max - file_freq_min) * fk_window_len
    # min_seq = max(2, int(min_duration / fk_window_len))
    min_seq = max(5, int(min_duration / fk_window_len))
    print(f"Min Sequence: {min_seq}")
    ######################################
    ##      Run detection analysis      ##
    ######################################
    #detect_signals(times, beam_results, win_len, TB_prod, channel_cnt, det_p_val=0.99, min_seq=5, back_az_lim=15, fixed_thresh=None, return_thresh=False)

    dets = beamforming_new.run_fd(beam_times, beam_peaks, det_win_len, TB_prod, channel_cnt, det_p_val=p_value, min_seq=min_seq)

    det_list = []
    for det_info in dets:
        det_list = det_list + [data_io.define_detection(det_info, [array_lat, array_lon], channel_cnt, [file_freq_min, file_freq_max], note="InfraPy CLI detection")]
    print(f"Writing detections to {local_detect_label}/{local_detect_label}_{freq_label}.dets.json")
    data_io.detection_list_to_json(f"./{date}/{local_detect_label}/{local_detect_label}_{freq_label}.dets.json", det_list)

    print('\n' + "Detection Summary:")
    dets_list = []
    for det in dets:
        print("Detection time:", det[0], '\t', "Rel. detection onset:", det[1], '\t',"Rel. detection end:", det[2], '\t',end=' ')
        print("Back azimuth:", np.round(det[3], 2), '\t', "Trace velocity:", np.round(det[4], 2), '\t', "F-stat:", np.round(det[5], 2), '\t', "Array dim:", channel_cnt)

    det_vis.plot_fk1(stream, lat_lon, beam_times, beam_peaks, detections=det_list, output_path=f"./{date}/{local_detect_label}/{local_detect_label}_{freq_label}.png", det_thresh=det_thresh, show_fig=True)

#### Construct Detection List
# det_list = []
# for det_info in dets:
#     det_list = det_list + [data_io.define_detection(det_info, [array_lat, array_lon], channel_cnt, [freq_min,freq_max], note="InfraPy CLI detection", method=method)]
# print("Writing detections to " + local_detect_label + ".dets.json")
# data_io.detection_list_to_json(local_detect_label + ".dets.json", det_list, stream_info)

# plt.figure()
# plt.suptitle("Detection results for analysis \n Filtered in frequency range: " + str(fk_freq_min) + " - " + str(fk_freq_max) + "  Hz \n ")

# x, t, t0, geom = beamforming_new.stream_to_array_data(read(sac_glob), latlon=lat_lon)
# M, N = x.shape

# for det in range(len(dets)):
#     dt = dets[det][0]-times[0] 
#     start = dt.item().total_seconds() 
#     ts = sig_start + start + dets[det][1]
#     te = sig_start + start + dets[det][2]
#     for m in range(M):
#         plt.subplot(M, 1, m + 1)
#         plt.xlim([sig_start, sig_end])
#         plt.plot(t, x[m], 'k-')
#         plt.axvspan(xmin = ts , xmax = te, alpha = 0.25, color = 'blue')
#         if m < (M - 1) : plt.setp(plt.subplot(M, 1, m + 1).get_xticklabels(), visible=False)
    
# plt.show()

    print("done")