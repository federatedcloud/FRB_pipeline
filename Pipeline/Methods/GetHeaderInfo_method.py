from method import *
from astropy.io import fits
from blimpy import Waterfall
from blimpy.io.sigproc import len_header

# Required parameters to put in the configuration file are:
#    directory, basename, filfile, mask_dir (if using maskdata)  

def main(hotpotato): 
    print("Getting Information from the Fits Header.")

    params_list= ['directory', 'basename', 'filetype']
    fil_params_list= ['filname_withhdr']
    print_params(params_list)

    directory= get_value(hotpotato, 'directory')
    filetype= get_value(hotpotato, 'filetype')

    if filetype == 'psrfits':
        fitsfile= directory + '/' + get_value(hotpotato, 'basename') + '.fits'
        hdulist = fits.open(fitsfile, ignore_missing_end=True)
        # Get Header Info and put it into a dictionary
        primaryDictionary = {}
        subintDictionary = {}
        primaryHeader = hdulist['PRIMARY'].header
        subintHeader = hdulist['SUBINT'].header
        for i in primaryHeader: 
            primaryDictionary[i] = primaryHeader[i]
        for j in subintHeader:
            subintDictionary[j] = subintHeader[j]
        # Add headers to input dictionary
        hotpotato.update(primaryDictionary)
        hotpotato.update(subintDictionary)

    elif filetype == 'filterbank':
        dictionary= {}
        filname= get_value(hotpotato, 'filname_withhdr')
        filfile= directory + '/' + filname
        # Get Header Info from filterbank file
        wat= Waterfall(filfile, load_data= False)
        header= wat.header
        for j in header:
            dictionary[str(j)[2:-1]]= header[j]
        dictionary['hdr_size']= len_header(filfile)
        print('Filterbank Header Info:\n\n')
        print(dictionary)
        hotpotato.update(dictionary)
        
    return hotpotato
