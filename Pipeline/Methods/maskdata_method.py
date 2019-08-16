from method import *

import os
import time
from glob import glob


def main(hotpotato):
    """
    Creates a masked dynamic spectrum called raw_data_with_mask.fits, 
    which is the file needed for modulation index
    """
    print("Creating masked dynamic spectrum...\n")
    t_md_start = time.time()
    
    # get/set file locations
    directory = get_value(hotpotato, 'directory')
    rfi_dir= get_value(hotpotato, 'rfi_dir')
    mask_dir= get_value(hotpotato, 'mask_dir')
    basename = get_value(hotpotato, 'basename')
    mask_name= get_value(hotpotato, 'filename_fil')

    # make sure rfifind has been run
    try:
        rfi_maskname = glob(rfi_dir+'/*rfifind.mask')[0] 
    except IndexError:
        raise Exception("Could not access RFI_masked fits file. Please run PRESTO rfifind "\
                       "before generating masked dynamic spectrum.")

    # set flags and run command
    #md_flags = d['md_flags']
    #md_otherflags = get_value(hotpotato, 'md_otherflags')
    filenamestr = directory + '/' + basename + '.fits'
    cmd = 'maskdata %s -mask %s %s %s' %(get_value(hotpotato, 'md_flags'), rfi_maskname, get_value(hotpotato, 'md_otherflags'), filenamestr)
    try_cmd(cmd)

    # move output to maskdata directory 
    if not os.path.exists(mask_dir):
        os.makedirs(mask_dir)

    # make sure -o flag is set in md_flags or md_otherflags
    o_index = cmd.find('-o')
    o_end = cmd.find(' ', o_index+3)
    file_str = cmd[o_index+3:o_end]
    
    mv_cmd1 = 'mv %s* %s' %(file_str, mask_dir)
    mv_cmd2 = 'mv %s %s' %(mask_name, mask_dir)
    try_cmd(mv_cmd1)
    try_cmd(mv_cmd2)
    
    t_md_end = time.time()
    time_md = t_md_end - t_md_start
    
    print("PRESTO maskdata took %f seconds." %(time_md))

    return hotpotato
