import numpy as np
import subprocess
from astropy.io import fits

def main(dictionary):
    print("Converting data to a numpy array")
    
    infile = dictionary['directory'] + '/' + dictionary['basename'] + '.fits'
    
    hdulist = fits.open(infile)
    
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
    dictionary.update(primaryDictionary)
    dictionary.update(subintDictionary)
    
    #TODO: do any necessary conversions here!
    
    
    # Get Data from FITS FILE
    hdu = hdulist[1]
    freqs = hdu.data[0]['dat_freq']
    dat = hdu.data[:]['data']
    
    if (dictionary['NBITS'] == 2):
        piece0 = np.bitwise_and(dat >> 6, 0x03)
        piece1 = np.bitwise_and(dat >> 4, 0x03)
        piece2 = np.bitwise_and(dat >> 2, 0x03)
        piece3 = np.bitwise_and(dat, 0x03)
        dat = np.dstack([piece0, piece1, piece2, piece3]).flatten()
    elif (dictionary['NBITS'] == 4):
        piece0 = np.bitwise_and(dat >> 4, 0x0F)
        piece1 = np.bitwise_and(dat, 0x0F)
        dat = np.dstack([piece0, piece1]).flatten()
    
    dd = np.reshape(dat, (-1, len(freqs)))
    dd = np.transpose(dd)
    
    # Save as .npz
    #print("Writing numpy array to disk...\n")
    #np.savez("combined_dynamic_spectra", dynamic_spectra=dd, primary_header = [primaryDictionary], subint_header = [subintDictionary]);
    #print("Write complete.")
    
    # TODO: don't do this when done testing (reduces numpy array to 0.5 seconds at the burst)
    data_array = dd
    dt = dictionary['TBIN']
    data_array = data_array[:, int(128.0/dt):int(128.5/dt)]
    
    # Add numpy array to input dictionary
    dictionary['np_data'] = data_array #npzfile
    
    return dictionary

