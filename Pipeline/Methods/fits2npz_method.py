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
    
    #TODO: do any necessary conversions here!
    
    # Get Data from FITS FILE
    hdu = hdulist[1]
    freqs = hdu.data[0]['dat_freq']
    dat = hdu.data[:]['data']
    #TODO: Is this splitting the data into 4-bit?  Make sure it only uses 4-bit data for Arecibo!
    piece0 = np.bitwise_and(dat >> 0x04, 0x0F)
    piece1 = np.bitwise_and(dat, 0x0F)
    dat = np.dstack([piece0, piece1]).flatten()
    dd = np.reshape(dat, (-1, len(freqs)))
    dd = np.transpose(dd)
    
    # Save as .npz
    #print("Writing numpy array to disk...\n")
    #np.savez("combined_dynamic_spectra", dynamic_spectra=dd, primary_header = [primaryDictionary], subint_header = [subintDictionary]);
    #print("Write complete.")
    
    # Add headers to input dictionary
    dictionary.update(primaryDictionary)
    dictionary.update(subintDictionary)
    
    # TEST - Reduce numpy array to 1 second (at the burst) for demo
    data_array = dd
    dt = dictionary['TBIN']
    data_array = data_array[:, int(128.0/dt):int(128.5/dt)]
    
    # Add numpy array to input dictionary
    dictionary['np_data'] = data_array #npzfile
    
    return dictionary

