#import sys
#sys.path.insert(0, '../MakeNPZ')
from astropy.io import fits
import numpy as np
import sys
import subprocess

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
    
    # Get Data from FITS FILE
    hdu = hdulist[1]
    freqs = hdu.data[0]['dat_freq']
    dat = hdu.data[:]['data']
    piece0 = np.bitwise_and(dat >> 0x04, 0x0F)
    piece1 = np.bitwise_and(dat, 0x0F)
    dat = np.dstack([piece0, piece1]).flatten()
    dd = np.reshape(dat, (-1, len(freqs)))
    dd = np.transpose(dd)
    
    # Save as .npz
    print("Writing numpy array to disk...\n")
    np.savez("combined_dynamic_spectra", dynamic_spectra=dd, primary_header = [primaryDictionary], subint_header = [subintDictionary]);
    print("Write complete.")
    
    # Add numpy array and headers to input dictionary
    npzfile = np.load("combined_dynamic_spectra.npz")
    dictionary['np_data'] = npzfile
    dictionary.update(primaryDictionary)
    dictionary.update(subintDictionary)
    
    #TEST
    print("\n\n Printing dictionary: \n")
    print(dictionary)
    print("\n\n End of dictionary \n\n")
    
    return dictionary

