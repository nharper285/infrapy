#!/usr/bin/env python

# test_bisl.py
#
# Author    Philip Blom (pblom@lanl.gov)

import numpy as np

from infrapy.location import bisl
from infrapy.utils import data_io
from infrapy.propagation import infrasound as infsnd
from infrapy.location import visualization as vis


# ######################### #
#       Define Inputs       #
# ######################### #

detection_label = "RAINIER-EVENT-C"
# Define localization parameters
bm_width = 12.5
rad_min, rad_max = 50.0, 500.0
rng_max = np.pi / 2.0 * 6370.0
resolution = int(np.sqrt(1e5))

# Load detection list from json file
det_list = data_io.json_to_detection_list(f'{detection_label}/{detection_label}-ev1.dets.json')

# Plot detections
vis.plot_dets_on_map(det_list)

# ########################## #
#          Run BISL          #
#       in Verbose Mode      #
# ########################## #

# Run analysis without priors
result = bisl.run(det_list,
                    bm_width=bm_width,
                    rad_min=rad_min, 
                    rad_max=rad_max, 
                    rng_max=rng_max, 
                    resol=resolution,angle=[-180,180])

print('-' * 75)
print('BISL Summary\n')
print(bisl.summarize(result))
print('\n' + '-'*75 + '\n')

# ###############################
# plot the results from bisl ####

vis.plot_loc(det_list, result)

# Define priors, load from file, and display
# model = infsnd.PathGeometryModel()
# model.load("../infrapy/propagation/priors/UTTR_models/UTTR_06_1800UTC.pgm")

# # Re-run analysis with priors
# result = bisl.run(det_list, 
#                     bm_width=bm_width,
#                     rad_min=rad_min, 
#                     rad_max=rad_max, 
#                     rng_max=rng_max, 
#                     resol=resolution,angle=[-180,180],
#                     path_geo_model=model)


# print('-' * 75)
# print('BISL Summary\n')
# print(bisl.summarize(result))
# print('\n' + '-'*75 + '\n')

# vis.plot_loc(det_list, result)
