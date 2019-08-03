from method import *

import time
from readhdr import get_samples
import psr_utils
from glob import glob

# Note: prepsubband is called as:
#       prepsubband -o 'outfile_name' 'input_files'

# Required parameters to put in the configuration file are:
#    downsample, prep_usemask, prep_flags, prep_otherflags

def main(hotpotato):

    print("Running PRETO prepsubband.")
    t_prep_start = time.time()

    # get/set file locations
    work_dir= get_value(hotpotato, 'directory')
    rfi_dir= get_value(hotpotato, 'rfi_dir')
    prep_dir = get_value(hotpotato, 'prep_dir')         # can change this
    basename = get_value(hotpotato, 'basename')
    fitslist = glob('%s/%s*.fits' %(rfi_dir, basename))
    fitslist.sort()
    fitsfiles = ' '.join(fitslist)
    
    # get de-dispersion parameters
    prep_usemask= get_value(hotpotato, 'prep_usemask')
    downsample= get_value(hotpotato, 'downsample')
    prep_flags= get_value(hotpotato, 'prep_flags')
    prep_otherflags = get_value(hotpotato, 'prep_otherflags')

    # run prepsubband command
    print("Dedispersing with 1st batch of DMs")
    orig_N = get_samples(fitslist, get_value(hotpotato, 'filetype'))
    numout = psr_utils.choose_N(orig_N) / downsample
    print(orig_N, numout)

    if prep_usemask == True:
        # make sure rfi_find has been run previously
        try:
            rfi_maskname = glob(rfi_dir+'/*.mask')[0]
        except IndexError:
            raise Exception("Could not access RFI_mask fits file. Please run PRESTO rfifind "\
                           "before generating masked dynamic spectrum.")

        cmd = 'prepsubband -o %s -numout %d %s %s -mask %s %s' %(basename, numout, 
                                                                 prep_flags, prep_otherflags, 
                                                                 rfi_maskname, fitsfiles)
    else:
        cmd = 'prepsubband -o %s %s %s %s' %(basename, numout, prep_flags, 
                                             prep_otherflags, fitsfiles) 

    try_cmd(cmd)

    # move output to prep_dir
    mv_cmd1 = 'mv %s %s' %(work_dir+'/*.dat', prep_dir)
    mv_cmd2 = 'mv %s %s' %(work_dir+'/*.inf', prep_dir)
    try_cmd(mv_cmd1)
    try_cmd(mv_cmd2)

    t_prep_end = time.time()
    prep_time = (t_prep_end - t_prep_start)
    print("PRESTO prepsubband took %f seconds." %(prep_time))

    return hotpotato
