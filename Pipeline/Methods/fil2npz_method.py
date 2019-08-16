from method import *
import numpy as np
import matplotlib.pyplot as plt
import subprocess
from astropy.io import fits

# Local Import:
import GetHeaderInfo_method

# Parameters used from dictionary:
#   directory, basename, mask_dir, mask_name, output_npz_file, npz_name, NCHAN, TBIN

def main(d):
    print("Converting data to a numpy array")
    
    # Maskdata used a special file
    if 'rfifind' in d['methods'] and 'maskdata' in d['methods']: 
        filfile= d['mask_dir'] + '/' + d['filename_fil']
    else:
        filfile= d['directory'] + '/' + d['filename_fil'] + '.fil'
    
    print("Using %s as filterbank file to convert" %(filfile) )
   
    d= GetHeaderInfo_method.main(d)

    # Put the data (from the filfile) in Numpy array
    dd = np.fromfile(filfile, dtype='float32')
    print(dd.shape)
    dd = np.reshape(dd, (-1, d['NCHAN'])).T
    dd = np.flip(dd, axis= 0)
    print(dd.shape)    
    
    # For Testing ONLY: reduce the size of the data
    if (d['testing_mode'] == True):
        dt = d['TBIN']
        dd = dd[:, int(128.0/dt):int(129.0/dt)]
    
    if (d['output_npz_file'] == True):
        save_npz(d['npz_name'], dd, [primaryDictionary], [subintDictionary])
        
    return d
