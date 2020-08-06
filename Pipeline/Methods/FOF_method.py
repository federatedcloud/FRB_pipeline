from method import *
from friends import *
import numpy as np

def main(hotpotato):
    print("Running Friend-Of-Friends")

    params_list= ['dec_name or npz_name', 'm1', 'm2', 't_gap', 'v_gap', 'tstart', 
               'fof_testing_mode', 'tsamp', 'vsamp', 'directory']
    fits_params_list= ['TBIN', 'CHAN_BW', 'OBSFREQ', 'NCHAN']
    print_params(params_list)
    print_fits_params(fits_params_list)
    
    # Set up fof-specific parameters
    try:
        dec_name= get_value(hotpotato, 'dec_name')
        data= np.load(dec_name + '.npy')
        print("Running Friend-Of-Friends on Decimated data.")
    except:
        print("Running Friend-Of-Friends NON-decimated data.")
        npz_file = np.load(get_value(hotpotato, 'npz_name') + '.npz')
        data= npz_file[npz_file.files[0]]
    print('Data Shape= ' + str(data.shape))

    m1 = get_value(hotpotato, 'm1')
    m2 = get_value(hotpotato, 'm2')
    t_gap = int(get_value(hotpotato, 't_gap'))
    v_gap = int(get_value(hotpotato, 'v_gap'))
    tstart = get_value(hotpotato, 'tstart')
    testing_mode = get_value(hotpotato, 'fof_testing_mode')
    filetype = get_value(hotpotato, 'filetype') 
   
    # set up dictionary of global parameters
    gd = {}
    if filetype == 'psrfits':
        dt= get_value(hotpotato, 'TBIN')
        dv= abs(get_value(hotpotato, 'CHAN_BW'))
        tsamp= int(get_value(hotpotato, 'tsamp'))
        vsamp= int(get_value(hotpotato, 'vsamp'))
        gd['tsamp']= tsamp
        gd['vsamp']= vsamp
        gd['vlow'] = get_value(hotpotato, 'OBSFREQ') - dv * get_value(hotpotato, 'NCHAN') / 2.0
        gd['vhigh'] = get_value(hotpotato, 'OBSFREQ') + dv * get_value(hotpotato, 'NCHAN') / 2.0
    elif filetype == 'filterbank':
        dt= get_value(hotpotato, 'tsamp')
        dv= abs(get_value(hotpotato, 'foff'))
        # Note the naming convention change:
        tcombine= int(get_value(hotpotato, 'tcombine'))
        vcombine= int(get_value(hotpotato, 'vcombine'))
        gd['tsamp']= tcombine
        gd['vsamp']= vcombine
        gd['vlow'] = get_value(hotpotato, 'fch1') - dv * get_value(hotpotato, 'nchans')
        gd['vhigh'] = get_value(hotpotato, 'fch1')
        gd['flip']= True
        #gd['vlow']= get_value(hotpotato, 'fch1') - dv * get_value(hotpotato, 'nchans')
        #gd['vhigh']= get_value(hotpotato, 'fch1')
    else:
        print('Filetype not recognized. Quitting... ')
        sys.exit()

    gd['dt']= dt
    gd['dv']= dv

   
    # Run algorithm
    fof(gd, data, m1, m2, t_gap, v_gap, tstart, testing_mode, False, 0)
    '''
    cmd= "mv *clust_* %s" %(get_value(hotpotato, 'directory'))
    try_cmd(cmd)
    '''
    return hotpotato
