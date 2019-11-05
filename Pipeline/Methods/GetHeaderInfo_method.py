from method import *
from astropy.io import fits

# Required parameters to put in the configuration file are:
#    directory, basename, filfile_name, mask_dir (if using maskdata)  

def main(hotpotato): 
    print("Getting Information from the Fits Header.")

    params_list= ['directory', 'basename']
    print_params(params_list)

    fitsfile= get_value(hotpotato, 'directory') + '/' + get_value(hotpotato, 'basename') + '.fits'
    hdulist = fits.open(fitsfile, ignore_missing_end=True)
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
    hotpotato.update(primaryDictionary)
    hotpotato.update(subintDictionary)

    return hotpotato
