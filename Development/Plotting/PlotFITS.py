#!/usr/bin/env python
from astropy.io import fits
import numpy as np
def plotFITS(file_name, start_time_sample, end_time_sample, combined=True):
    """
    Made by Shiva Lakshmanan 2018
    
    Here is a function to plot FITS file at a given time stamp range.
    The combined parameter is for if the FITS file has been run through
    combine_mocks, which is a program the combine subbands of the Arecibo
    Telescope into one coherent data file that contains all frequency channels
    of the Arecibo Telescope.
    
    Note: if you want to calculate time samples. You need the time sample size.
    called that x. Say you want 100s to 150s. the start time sample is
    100/x and the end time sample is 150/x. MAKE SURE TO CAST THOSE NUMBERS TO INTEGERS
    Because we need them to be indices of an array, so they must be integers. 
    """    
    infile = file_name #the name of the file
    hdulist = fits.open(infile) #we open the file
    if not combined:
        hdu = hdulist[3] #access the data
        freqs = hdu.data[0]['dat_freq'] #a list of the frequency channels
        dat = hdu.data[:]['data'] #the actual data array
        
        #We have to unpack the data because we are storing 4 bit data into 8 bit data in order to save space.
        #Don't worry too much about this step, just think of it like unzipping a file
        piece0 = np.bitwise_and(dat >> 0x04, 0x0F) 
        piece1 = np.bitwise_and(dat, 0x0F)
        dat = np.dstack([piece0, piece1]).flatten()
        
        dd = np.reshape(dat, (-1, len(freqs))) #each row of the data(if you think of it as a matrix) is 1 second time bins.
                                               #But we want each row to contain 1 time sample worth of data, so we have to reshape the data array
        dd = dd[start_time_sample:end_time_sample] #Select the time sample range you want to plot from  
        dd = np.transpose(dd) #Data array was originally time on the y axis, frequency on the x axis. We want time on the x axis and frequency on the y axis, so we take the transpose
        imshow(dd, aspect="auto", origin="lower", interpolation="nearest") #plot the data 
        colorbar() #display a colorbar scale
    else:
        #same comments apply here, but just a little different
        hdu = hdulist[1]
        freqs = hdu.data[0]['dat_freq']
        dat = hdu.data[:]['data']
        piece0 = np.bitwise_and(dat >> 0x04, 0x0F)
        piece1 = np.bitwise_and(dat, 0x0F)
        dat = np.dstack([piece0, piece1]).flatten()
        dd = np.reshape(dat, (-1, len(freqs)))
        dd = dd[start_time_sample:end_time_sample]
        dd = np.transpose(dd)
        imshow(dd, aspect="auto", origin="lower", interpolation="nearest")
        colorbar()
