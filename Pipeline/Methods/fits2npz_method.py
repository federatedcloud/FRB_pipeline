from method import *
import numpy as np
import subprocess
from astropy.io import fits

def main(dictionary):
    print("Converting data to a numpy array")
    
    infile = dictionary['directory'] + '/' + dictionary['basename'] + '.fits'
    
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
    dictionary.update(primaryDictionary)
    dictionary.update(subintDictionary)
    
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
    
    # For Testing ONLY: reduce the size of the data
    if (dictionary['testing_mode'] == True):
        dt = dictionary['TBIN']
        dd = dd[:, int(128.0/dt):int(128.5/dt)]
    
    if (dictionary['output_npz_file'] == True):
        print("Writing numpy array to disk...\n")
        save_npz(dictionary['npz_name'], dd, [primaryDictionary], [subintDictionary])
        print("Write complete.")
    
    return dictionary

# Don't need this
# Save dynamic spectra and headers as .npz file
def save_npz(npzfilename, dynamic_spectra, primary_header, subint_header):
    print("Writing numpy array to disk...\n")
    
    if (npzfilename == ""):
        npzfilename = "output_dynamic_spectra"
    
    np.savez(npzfilename, dynamic_spectra, primary_header, subint_header);
    
    print("Write complete.")
    return

