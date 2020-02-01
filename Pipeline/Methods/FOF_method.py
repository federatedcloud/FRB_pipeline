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
        print("Running Friend-Of-Friends on Decimated data.")
        data= np.load(dec_name + '.npy')
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
    
    # set up dictionary of global parameters
    gd = {} 
    gd['tsamp'] = int(get_value(hotpotato, 'tsamp'))
    gd['vsamp'] = int(get_value(hotpotato, 'vsamp'))
    gd['dt'] = get_value(hotpotato, 'tbin')
    gd['dv'] = abs(get_value(hotpotato, 'CHAN_BW')) # for some reason this was negative
    dv = gd['dv']
    gd['vlow'] = get_value(hotpotato, 'OBSFREQ') - dv * get_value(hotpotato, 'NCHAN') / 2.0
    gd['vhigh'] = get_value(hotpotato, 'OBSFREQ') + dv * get_value(hotpotato, 'NCHAN') / 2.0
    
    # Run algorithm
    fof(gd, data, m1, m2, t_gap, v_gap, tstart, testing_mode)
    
    cmd= "mv *clust_* %s" %(get_value(hotpotato, 'directory'))
    try_cmd(cmd)

    return hotpotato
