from method import *
import numpy as np
import matplotlib.pyplot as plt
import subprocess
from astropy.io import fits

# Parameters used from dictionary:
#   directory, basename, mask_dir, mask_name, output_npz_file, npz_name, NCHAN, TBIN

def main(d):
    print("Converting data to a numpy array")

    fitsfile= d['directory'] + '/' + d['basename'] + '.fits' 
    
    # Maskdata used a special file
    if 'rfifind' in d['methods'] and 'maskdata' in d['methods']: 
        filfile= d['mask_dir'] + '/' + d['filfile_name']
    else:
        filfile= d['directory'] + '/' + d['filfile_name'] + '.fil'
    
    print("Using %s as filterbank file to convert" %(filfile) )
    
    hdulist = fits.open(fitsfile, ignore_missing_end=True)
    
    # Get Header Info and put it into a d
    primaryDictionary = {}
    subintDictionary = {}
    primaryHeader = hdulist[0].header
    subintHeader = hdulist[1].header
    for i in primaryHeader:
        primaryDictionary[i] = primaryHeader[i]
    for j in subintHeader:
        subintDictionary[j] = subintHeader[j]
    
    # Add headers to input dictionary
    d.update(primaryDictionary)
    d.update(subintDictionary)
    
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
