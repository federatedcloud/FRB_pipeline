from method import *
import numpy as np
from astropy.io import fits

# Local Import:
import GetHeaderInfo_method

# Required parameters to put in the configuration file are:
#   directory, basename, mask_dir, filfile, output_npz_file, npz_name, NCHAN, TBIN
# Note: other parameters are obtained from header files (stored in hotpotato)

def main(hotpotato):
    print("Converting data to a numpy array")

    # Get Header Info    
    hotpotato= GetHeaderInfo_method.main(hotpotato)
    
    # Maskdata used a special file
    if 'rfifind' in get_value(hotpotato, 'methods') and 'maskdata' in get_value(hotpotato, 'methods'): 
        filfile = get_value(hotpotato, 'mask_dir') + '/' + get_value(hotpotato, 'filfile')
    else:
        filfile = get_value(hotpotato, 'directory') + '/' + get_value(hotpotato, 'filfile') + '.fil'
    print("Using %s as filterbank file to convert" %(filfile) )

    # Put the data (from the filfile) in Numpy array
    dd = np.fromfile(filfile, dtype='float32')
    dd = np.reshape(dd, (-1, get_value(hotpotato, 'NCHAN'))).T
    dd = np.flip(dd, axis= 0)
    
    # For Testing ONLY: reduce the size of the data
    if (get_value(hotpotato, 'testing_mode') == True):
        dt = get_value(hotpotato, 'TBIN')
        dd = dd[:, int(128.0/dt):int(129.0/dt)]
    
    if (get_value(hotpotato, 'output_npz_file') == True):
        save_npz(get_value(hotpotato, 'npz_name'), dd)
        
    return hotpotato
