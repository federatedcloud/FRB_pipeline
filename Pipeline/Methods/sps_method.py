# single pulse search method
from method import *

import time
from glob import glob
import os

def main(d):

    print("Looking for single pulse...\n")
    t_sp_start = time.time()
    # get/set file locations
    
    work_dir = d['work_dir']
    prep_dir = work_dir + d['prep_dir_name']
    sp_dir = work_dir + d['sp_dir_name']
    cl_dir = work_dir + d['cl_dir_name']

    # make sure prepsubband has been run
    try:
        dat_files = glob(prep_dir+'/*.dat')[0]
    except IndexError:
        raise Exception("Could not access de-dispersed time-series data files. Please run PRESTO prepsubband before searching for single pulses.")

    # single pulse search parameters
    sp_exe = d['sp_exe'] # params.singlepulse
    w_max = d['w_max']  # params.max_width
    sp_otherflags = d['sp_otherflags']
    cl_width = d['cl_width'] # params.cluster_width
    cl_bins = int(cl_width / float(d['dt']))

    # run the command
    cmd = "%s %s -p -m %.6f -w %d %s/*.dat" %(sp_exe, sp_otherflags, w_max, cl_bins, work_dir)

    try_cmd(cmd)

    # move output files to appropraite directories
    if not os.path.exists(sp_dir):
        os.makedirs(sp_dir)

    cmd_mv1 = 'mv %s %s' %(work_dir)
    try_cmd(cmd_mv)

    if not os.path.exists(cl_dir):
        os.makedirs(cl_dir)

    cmd_mv2 = 'mv %s %s' %(work_dir+'/*.cluster', cl_dir)

    t_sp_end = time.time()
    print("Single pulse searching took %.2f seconds" %(t_sp_end-t_sp_start))

