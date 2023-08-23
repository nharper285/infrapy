#!/usr/bin/env python -W ignore::DeprecationWarning

# test_assoc.py
#
# Author    Philip Blom (pblom@lanl.gov)

import numpy as np

import pathos.multiprocessing as mp
from multiprocessing import cpu_count

from infrapy.association import hjl
from infrapy.utils import data_io

from multiprocess import Pool


if __name__ == '__main__':
    #########################
    ### Define parameters ###
    #########################
    loc_event_label = "RAINIER-EVENT-A"
    date = "8-15-2023"
    # Read in detections from file
    det_list = data_io.set_det_list(f'./{date}/{loc_event_label}/*', merge=True)

    # define clustering parameters
    back_az_width = 10.0
    range_max = 2000.0
    resolution = 180
    distance_matrix_max = 10.0
    cluster_linkage = "weighted"
    cluster_threshold = 5.0
    trimming_threshold = 3.0
    
    # dist_max = 8.0
    # clustering_threshold = 7.0
    # trimming_thresh = 3.8
    
    starttime = None
    endtime = None
    
    pl = Pool(cpu_count() - 1)
    ######################
    #### Run analysis ####
    ######################
    events, event_qls = hjl.id_events(det_list, cluster_threshold, starttime=starttime, endtime=endtime, dist_max=distance_matrix_max, 
                                    bm_width=back_az_width, rng_max=range_max, rad_min=100.0, rad_max=(range_max / 4.0), 
                                    resol=resolution, linkage_method=cluster_linkage, trimming_thresh=trimming_threshold, 
                                    pool=pl)
    
    data_io.write_events(events, event_qls, det_list, f"./{date}/{loc_event_label}/{loc_event_label}")    
    print("Identified " + str(len(events)) + " events." + '\n')
    
    # Graph Analysis
    labels, dists = hjl.run(det_list, cluster_threshold, dist_max=distance_matrix_max, bm_width=back_az_width, rng_max=range_max, trimming_thresh=trimming_threshold, pool=pl,show_result=True)
    # Summarize clusters
    clusters, qualities = hjl.summarize_clusters(labels, dists)
    for n in range(len(clusters)):
        print("Cluster:", clusters[n], '\t', "Cluster Quality:", 10.0**(-qualities[n]))
        
    pl.close()
    pl.terminate()






