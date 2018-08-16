#!/usr/bin/env python3
'''
Made by Shiva Lakshmanan May 30th 2018
Script to combine to Arecibo FITS files, unpack the data,
and save it as a .npz file at full resolution

variables are as follows:
dynamic_spectra
primary_header
subint_header
'''
from astropy.io import fits
import numpy as np
import sys
import subprocess

file1 = sys.argv[1]
file2 = sys.argv[2]
outbasenm = file1[:len(file1)-4] + "combined"
mergecmd = "combine_mocks %s %s -o %s" % (file1, file2, outbasenm) #command for combine mocks
subprocess.check_call([mergecmd], shell=True)

    
#Load in data
infile = outbasenm + "_0001.fits"
hdulist = fits.open(infile)
    
#Get Header Info and put it into a dictionary
primaryDictionary = {}
subintDictionary = {}
primaryHeader = hdulist[0].header
subintHeader = hdulist[1].header
for i in primaryHeader:
    primaryDictionary[i] = primaryHeader[i]
for j in subintHeader:
    subintDictionary[j] = subintHeader[j]
    
#Get Data from FITS FILE
hdu = hdulist[1]
freqs = hdu.data[0]['dat_freq']
dat = hdu.data[:]['data']
piece0 = np.bitwise_and(dat >> 0x04, 0x0F)
piece1 = np.bitwise_and(dat, 0x0F)
dat = np.dstack([piece0, piece1]).flatten()
dd = np.reshape(dat, (-1, len(freqs)))
dd = np.transpose(dd)
    
'''
I put header information into a dictionary and then put that into an array, so that we can work with only an npz file.
You can access it by:
npzfile = np.load("combined_dynamic_spectra.npz")
npzfile["primary_header"][0] (need to just access the only element in the array to access the dictionary)
'''

np.savez("combined_dynamic_spectra", dynamic_spectra=dd, primary_header = [primaryDictionary], subint_header = [subintDictionary]);
