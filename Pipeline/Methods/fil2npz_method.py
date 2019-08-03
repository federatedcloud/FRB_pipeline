from method import *
import numpy as np
from astropy.io import fits

# Required parameters to put in the configuration file are:
#   directory, basename, mask_dir, filfile_name, output_npz_file, npz_name, NCHAN, TBIN
# Note: other parameters are obtained from header files (stored in hotpotato)

def main(hotpotato):
    print("Converting data to a numpy array")

    fitsfile = get_value(hotpotato, 'directory') + '/' + get_value(hotpotato, 'basename') + '.fits' 
    
    # Maskdata used a special file
    if 'rfifind' in get_value(hotpotato, 'methods') and 'maskdata' in get_value(hotpotato, 'methods'): 
        filfile = get_value(hotpotato, 'mask_dir') + '/' + get_value(hotpotato, 'filfile_name')
    else:
        filfile = get_value(hotpotato, 'directory') + '/' + get_value(hotpotato, 'filfile_name') + '.fil'
    
    print("Using %s as filterbank file to convert" %(filfile) )
    
    hdulist = fits.open(fitsfile, ignore_missing_end=True)
    
    # Get Header Info and put it into a dictionary 
    primaryDictionary = {}
    subintDictionary = {}
    primaryHeader = hdulist[0].header
    subintHeader = hdulist[1].header
    for i in primaryHeader:
        primaryDictionary[i] = primaryHeader[i]
    for j in subintHeader:
        subintDictionary[j] = subintHeader[j]
    
    # Add headers to input dictionary
    hotpotato.update(primaryDictionary)
    hotpotato.update(subintDictionary)
    
    # Put the data (from the filfile) in Numpy array
    dd = np.fromfile(filfile, dtype='float32')
    print(dd.shape)
    dd = np.reshape(dd, (-1, get_value(hotpotato, 'NCHAN'))).T
    dd = np.flip(dd, axis= 0)
    print(dd.shape) 
    
    # For Testing ONLY: reduce the size of the data
    if (get_value(hotpotato, 'testing_mode') == True):
        dt = get_value(hotpotato, 'TBIN')
        dd = dd[:, int(128.0/dt):int(129.0/dt)]
    
    if (get_value(hotpotato, 'output_npz_file') == True):
        save_npz(get_value(hotpotato, 'npz_name'), dd, [primaryDictionary], [subintDictionary])
        
    return hotpotato

