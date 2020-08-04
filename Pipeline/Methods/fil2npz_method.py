from method import *
from read_fil import *
import numpy as np
from blimpy import Waterfall
from blimpy.io.sigproc import len_header

# Required parameters to put in the configuration file are:
#   directory, basename, mask_dir, filfile, output_npz_file, npz_name, NCHAN, TBIN
# Note: other parameters are obtained from header files (stored in hotpotato)

def main(hotpotato):
    print("Converting data to a numpy array")

    # Note: methods should always be in config file
    params_list= ['methods', 'filname', 'directory', 
                  'output_npz_file', 't_start', 't_stop', 'npz_name']
    fil_params_list= ['nifs', 'NBITS', 'nchans', 'hdr_size']
     
    print_params(params_list)
    print_fil_params(fil_params_list)
    
    filetype= get_value(hotpotato, 'filetype')
    if filetype=='psrfits':
        set_value(hotpotato, 'nifs', get_value(hotpotato, 'NPOL'))
        set_value(hotpotato, 'nbits', get_value(hotpotato, 'NBITS'))
        set_value(hotpotato, 'nchans', get_value(hotpotato, 'NCHAN'))
        set_value(hotpotato, 'hdr_size', 0)
 
    filname= get_value(hotpotato, 'filname')
    directory= get_value(hotpotato, 'directory') 
    t_start= get_value(hotpotato, 't_start')
    t_stop= get_value(hotpotato, 't_stop')

    filfile= directory + '/' + filname
    # Get Header Info from filterbank file

    #wat= Waterfall(filfile, load_data= False)
    #header= wat.header
    #n_ifs= header[b'nifs']
    #n_bytes= header[b'NBITS'] / 8
    #nchans= header[b'nchans']
    #hdr_size= len_header(filfile)

    n_ifs= get_value(hotpotato, 'nifs')
    n_bytes= get_value(hotpotato, 'NBITS') / 8
    nchans= get_value(hotpotato, 'nchans')
    hdr_size= get_value(hotpotato, 'hdr_size')
    f= open(filfile, 'rb')
    
    # For Testing ONLY: reduce the size of the data
    if (get_value(hotpotato, 'testing_mode') == True):
        dt = get_value(hotpotato, 'TBIN')
        t_start = int(128.0/dt)
        t_stop = int(128.5/dt)
    
    print('f: ' + str(f))
    print('hdr_size: ' + str(hdr_size))
    print('t_start: ' + str(t_start))

    dd= load_fil_data(filname, directory, t_start, t_stop, n_ifs, nchans, n_bytes, f, hdr_size, pol=[0], current_cursor_position=0)

    print(dd.shape)
    dd= dd[0]
    print(dd.shape) 
    if (get_value(hotpotato, 'output_npz_file') == True):
        save_npz(get_value(hotpotato, 'npz_name'), dd)
        
    return hotpotato
