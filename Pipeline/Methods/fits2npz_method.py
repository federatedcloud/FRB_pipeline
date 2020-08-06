from method import *
import numpy as np
import subprocess
from astropy.io import fits

# Local Import
import GetHeaderInfo_method
    
def main(hotpotato):
    print("Converting data to a numpy array") 

    params_list= ['directory', 'basename', 'testing_mode', 'output_npz_file', 'npz_name']
    fits_params_list= ['NBITS', 'TBIN']
    print_params(params_list)
    print_fits_params(fits_params_list)
    
    # Get Header Info
    hotpotato = GetHeaderInfo_method.main(hotpotato)

    # Get Data from Fits file
    #infile = get_value(hotpotato, 'directory') + '/' + get_value(hotpotato, 'basename') + '.fits'
    infile = get_value(hotpotato, 'directory') + '/' + 'raw_data_with_mask.fits'
    hdulist = fits.open(infile, ignore_missing_end=True)
    #hdu = hdulist['SUBINT']
    #freqs = hdu.data[0]['dat_freq']
    #dat = hdu.data['DATA']
    hdu = hdulist[1]
    freqs = hdu.data[0]['dat_freq']
    data = hdu.data[:]['data']
    '''
    print('FITS dat shape: ' + str(dat.shape))
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
    print('FITS flattened dat shape: ' + str(dat.shape))
    
    dd = np.reshape(dat, (-1, len(freqs)))
    dd = np.transpose(dd)
    print('Numpy reshaped: ' + str(dd.shape))   
 
    # For Testing ONLY: reduce the size of the data
    if (get_value(hotpotato, 'testing_mode') == True):
        dt = get_value(hotpotato, 'TBIN')
        dd = dd[:, int(128.0/dt):int(128.5/dt)]
    
    print("Testing Mode reduced shape: " + str(dd.shape))
    '''
    data = data.reshape((data.shape[0]*data.shape[1],data.shape[2],data.shape[3])) # (Ntsamples, NPOL, NCHANS)
    data = np.moveaxis(data,0,-1) # Move time samples to last axis of array.
    data = data[0]   # Select required polarization. Data shape = (NCHANS, Ntsamples)
    print('Data shape:', data.shape)
    
    if (get_value(hotpotato, 'output_npz_file') == True):
        save_npz(get_value(hotpotato, 'npz_name'), data)
    

    return hotpotato
