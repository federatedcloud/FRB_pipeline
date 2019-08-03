# single pulse search method
from method import *

import time
from glob import glob
import os

def main(hotpotato):

    print("Looking for single pulse...\n")
    t_sp_start = time.time()

    # get/set file locations
    work_dir = get_value(hotpotato, 'directory')
    prep_dir = get_value(hotpotato, 'prep_dir')
    sp_dir = get_value(hotpotato, 'sp_dir')
    cl_dir = get_value(hotpotato, 'cl_dir')

    # make sure prepsubband has been run
    try:
        dat_files = glob(prep_dir+'/*.dat')[0]
    except IndexError:
        raise Exception("Could not access de-dispersed time-series data files. Please run PRESTO prepsubband before searching for single pulses.")

    # single pulse search parameters
    sp_exe = get_value(hotpotato, 'sp_exe') # params.singlepulse
    sp_flags= get_value(hotpotato, 'flags')
    sp_otherflags = get_value(hotpotato, 'sp_otherflags')
    sp_modified= get_value(hotpotato, 'sp_modified')

    # run the command
    if sp_modified == True: #use Spitler's mod_sp.py with fixed flags
        w_max= get_value(hotpotato, 'w_max')
        cl_width= get_value(hotpotato, 'cl_width') # params.cluster_width
        cl_bins= int(cl_width / float(get_value(hotpotato, 'TBIN')))
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
    
    return hotpotato

