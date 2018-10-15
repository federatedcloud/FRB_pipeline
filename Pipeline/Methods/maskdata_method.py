from method import *

import os
import time
from glob import glob


def main(d):
    """
    Creates a masked dynamic spectrum called raw_data_with_mask.fits, 
    which is the file needed for modulation index
    """
    print("Creating masked dynamic spectrum...\n")
    t_md_start = time.time()
    
    # get/set file locations
    basename = d['basename']
    work_dir = d['work_dir']
    fits_dir = d['directory']
    rfi_dir = work_dir + d['rfi_dir_name']
    maskdata_dir = work_dir + d['maskdata_dir_name']

    # make sure rfifind has been run
    try:
        rfi_maskname = glob(rfi_dir+'/*.mask')[0] 
    except IndexError:
        raise Exception("Could not access RFI_masked fits file. Please run PRESTO rfifind "\
                       "before generating masked dynamic spectrum.")

    # set flags and run command
    #md_flags = d['md_flags']
    #md_otherflags = d['md_otherflags']
    filenamestr = fits_dir + '/' + basename + '.fits'
    cmd = 'maskdata %s %s %s %s' %(d['md_flags'], rfi_maskname, d['md_otherflags'], filenamestr)
    try_cmd(cmd)

    # move output to maskdata directory 
    if not os.path.exists(maskdata_dir):
        os.makedirs(maskdata_dir)

    # make sure -o flag is set in md_flags or md_otherflags
    o_index = cmd.find('-o')
    o_end = cmd.find(' ', o_index+3)
    file_str = cmd[o_index+3:o_end]

    mv_cmd1 = 'mv %s* %s' %(file_str, maskdata_dir)
    mv_cmd2 = 'mv raw_data_with_mask.fits %s' %(maskdata_dir)
    try_cmd(mv_cmd1)
    try_cmd(mv_cmd2)

    t_md_end = time.time()
    time_md = t_md_end - t_md_start
    
    d['masked_data'] = 'raw_data_with_mask.fits'
    print("PRESTO maskdata took %f seconds." %(time_md))

    return d
