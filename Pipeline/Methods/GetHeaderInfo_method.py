from method import *
from astropy.io import fits

'''
Requires the following parameters from .cfg file:
    directory, basename, mask_dir, mask_name
'''

def main(d): 
    print("Getting Information from the Fits Header.")

    fitsfile= d['directory'] + '/' + d['basename'] + '.fits'

    # Maskdata used a special file
    if 'rfifind' in d['methods'] and 'maskdata' in d['methods']:
        filfile= d['mask_dir'] + '/' + d['mask_name']
    else:
        filfile= d['mask_dir'] + '/' + d['mask_name'] + '.fil'

    filfile= d['mask_dir'] + '/' + d['mask_name']
    print("Using %s as filterbank file to convert" %(filfile) ) 
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
