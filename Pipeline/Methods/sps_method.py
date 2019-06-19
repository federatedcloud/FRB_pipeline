# single pulse search method
from method import *

import time
from glob import glob
import os

def main(d):

    print("Looking for single pulse...\n")
    t_sp_start = time.time()

    # get/set file locations
    work_dir = d['directory']
    prep_dir = d['prep_dir']
    sp_dir = d['sp_dir']
    cl_dir = d['cl_dir']

    # make sure prepsubband has been run
    try:
        dat_files = glob(prep_dir+'/*.dat')[0]
    except IndexError:
        raise Exception("Could not access de-dispersed time-series data files. Please run PRESTO prepsubband before searching for single pulses.")

    # single pulse search parameters
    sp_exe = d['sp_exe'] # params.singlepulse
    sp_flags= d['flags']
    sp_otherflags = d['sp_otherflags']
    sp_modified= d['sp_modified']

    # run the command
    if sp_modified == True: #use Spitler's mod_sp.py with fixed flags
        w_max= d['w_max']
        cl_width= d['cl_width'] # params.cluster_width
        cl_bins= int(cl_width / float(d['TBIN']))
        cmd = '%s %s -p -m %.6f -w %d %s/*.dat' %(sp_exe, sp_otherflags, w_max, cl_bins, work_dir)
    else:
        cmd = '%s %s %s %s/*.dat' %(sp_exe, sp_otherflags, sps_flags, prep_dir)

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

