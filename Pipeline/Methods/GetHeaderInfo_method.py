from method import *
from astropy.io import fits

'''
Requires the following parameters from .cfg file:
    directory, basename, mask_dir, mask_name
'''

def main(d): 
    print("Getting Information from the Fits Header.")

    fitsfile= d['directory'] + '/' + d['basename'] + '.fits'
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

    return d
