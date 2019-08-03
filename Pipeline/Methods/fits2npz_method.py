from method import *
import numpy as np
import subprocess
from astropy.io import fits

def main(hotpotato):
    print("Converting data to a numpy array")
    
    infile = get_value(hotpotato, 'directory') + '/' + get_value(hotpotato, 'basename') + '.fits'
    
    hdulist = fits.open(infile, ignore_missing_end=True)
    
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
    
    # Get Data from FITS FILE
    hdu = hdulist[1]
    freqs = hdu.data[0]['dat_freq']
    dat = hdu.data[:]['data']
    
    if (get_value(hotpotato, 'NBITS') == 2):
        piece0 = np.bitwise_and(dat >> 6, 0x03)
        piece1 = np.bitwise_and(dat >> 4, 0x03)
        piece2 = np.bitwise_and(dat >> 2, 0x03)
        piece3 = np.bitwise_and(dat, 0x03)
        dat = np.dstack([piece0, piece1, piece2, piece3]).flatten()
    elif (get_value(hotpotato, 'NBITS') == 4):
        piece0 = np.bitwise_and(dat >> 4, 0x0F)
        piece1 = np.bitwise_and(dat, 0x0F)
        dat = np.dstack([piece0, piece1]).flatten()
    
    dd = np.reshape(dat, (-1, len(freqs)))
    dd = np.transpose(dd)
    
    # For Testing ONLY: reduce the size of the data
    if (get_value(hotpotato, 'testing_mode') == True):
        dt = get_value(hotpotato, 'TBIN')
        dd = dd[:, int(128.0/dt):int(128.5/dt)]
    
    if (get_value(hotpotato, 'output_npz_file') == True):
        save_npz(get_value(hotpotato, 'filename_npz'), dd, [primaryDictionary], [subintDictionary])
    
    return hotpotato

