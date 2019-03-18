from method import *
import numpy as np
import subprocess
from astropy.io import fits

def main(d):
    print("Converting data to a numpy array")

    filfile= d['directory'] + '/' + 'raw_data_with_mask.fits'
    fitsfile= d['directory'] + '/' + d['basename'] + '.fits' 

    if 'rfifind' in d['methods'] and 'maskdata' in d['methods']:    
        # possibly a print message
    else:
        # possibly a print message 

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
    dd = np.reshape(dd, (-1, nchan))
    print(dd.shape)    

    if (d['output_npz_file'] == True):
        save_npz(d['filename_npz'], dd, [primaryDictionary], [subintDictionary])
    
    # TODO: don't do this when done testing (reduces numpy array to 0.5 seconds at the burst)
    data_array = dd
    dt = d['TBIN']
    data_array = data_array[:, int(128.0/dt):int(128.5/dt)]
    
    # Add numpy array to input dictionary
    d['np_data'] = data_array
    
    return d

# Save dynamic spectra and headers as .npz file
def save_npz(npzfilename, dynamic_spectra, primary_header, subint_header):
    print("Writing numpy array to disk...\n")
    
    if (npzfilename == ""):
        npzfilename = "output_dynamic_spectra"
    
    np.savez(npzfilename, dynamic_spectra, primary_header, subint_header);
    
    print("Write complete.")
    return

