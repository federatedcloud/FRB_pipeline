import numpy as np
import pdat
from astropy.io import fits

def main(hotpotato):
    print("Converting numpy array to psrfits file")
    
    outfile = get_value(hotpotato, 'directory') + '/' + get_value(hotpotato, 'basename') + '_generated.fits'
    
    
    
    return hotpotato

