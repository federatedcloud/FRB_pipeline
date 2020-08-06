from method import *
import sys
import os
import time
from glob import glob


def main(hotpotato):
    """
    Creates a masked dynamic spectrum called raw_data_with_mask.fits, 
    which is the file needed for modulation index
    """
    print("Creating masked dynamic spectrum...\n")
   
    params_list= ['directory', 'rfi_dir', 'mask_dir', 'basename', 'filname_withhdr', 
                  'md_flags', 'md_otherflags']
    print_params(params_list)

    t_md_start = time.time()
    
    # get/set file locations
    directory = get_value(hotpotato, 'directory')
    filetype= get_value(hotpotato, 'filetype')
    filname_withhdr= get_value(hotpotato, 'filname_withhdr')
    rfi_dir= get_value(hotpotato, 'rfi_dir')
    mask_dir= get_value(hotpotato, 'mask_dir')
    basename = get_value(hotpotato, 'basename')
    mask_name= get_value(hotpotato, 'filname')

    # make sure rfifind has been run
    try:
        rfi_maskname = glob(rfi_dir+'/*rfifind.mask')[0] 
    except IndexError:
        raise Exception("Could not access RFI_masked fits file. Please run PRESTO rfifind "\
                       "before generating masked dynamic spectrum.")

    # set flags and run command
    if filetype == 'psrfits':
        filenamestr = directory + '/' + basename + '.fits'
    elif filetype == 'filterbank':
        filenamestr= directory + '/' + filname_withhdr
    else:
        print('Filetype not recognized. Quitting...')
        sys.exit()

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
    mv_cmd2 = 'mv %s %s/%s' %(mask_name, directory, mask_name)
    try_cmd(mv_cmd1)
    try_cmd(mv_cmd2)
    
    # allows use of fil2npz when working with a fits header
    set_value(hotpotato, 'nifs', get_value(hotpotato, 'NPOL'))
    set_value(hotpotato, 'nbits', get_value(hotpotato, 'NBITS'))
    set_value(hotpotato, 'nchans', get_value(hotpotato, 'NCHAN'))
    set_value(hotpotato, 'hdr_size', 0)
    
    # Output a masked dynamic spectra in the form of an npz file
    #print("NOTE: fil2npz_method is being used to output a masked dynamic spectra as an npz file.\n")
    #temp = __import__('fil2npz_method')
    #hotpotato = temp.main(hotpotato)
    
    t_md_end = time.time()
    time_md = t_md_end - t_md_start

    print("PRESTO maskdata took %f seconds." %(time_md))

    return hotpotato
