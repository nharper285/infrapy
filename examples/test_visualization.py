import numpy as np

import pathos.multiprocessing as mp
from multiprocessing import cpu_count
from multiprocess import Pool
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from obspy.core import read

from scipy import signal

from infrapy.detection import beamforming_new
from infrapy.detection import visualization as det_vis

if __name__ == '__main__':
    sac_glob = "KAUT/*.SAC"
    lat_lon = np.load("./KAUT/KAUT.npy")