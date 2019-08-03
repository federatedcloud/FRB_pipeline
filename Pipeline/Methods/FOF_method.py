from method import *
from friends import *
import numpy as np

def main(hotpotato):
    print("Running Friend-Of-Friends")
    
    # Set up fof-specific parameters
    try:
        dec_name= get_value(hotpotato, 'dec_name')
        print("Running Friend-Of-Friends on Decimated data.")
        dec_file= np.load(dec_name + '.npz')
        data= dec_file[dec_file.files[0]]
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
    
    # set up dictionary of global parameters
    gd = {} 
    gd['tsamp'] = int(get_value(hotpotato, 'tsamp'))
    gd['vsamp'] = int(get_value(hotpotato, 'vsamp'))
    gd['dt'] = get_value(hotpotato, 'TBIN')
    gd['dv'] = abs(get_value(hotpotato, 'CHAN_BW')) # for some reason this was negative
    dv = gd['dv']
    gd['vlow'] = get_value(hotpotato, 'OBSFREQ') - dv * get_value(hotpotato, 'NCHAN') / 2.0
    gd['vhigh'] = get_value(hotpotato, 'OBSFREQ') + dv * get_value(hotpotato, 'NCHAN') / 2.0
    
    # Run algorithm
    fof(gd, data, m1, m2, t_gap, v_gap, tstart)
    
    cmd= "mv *clust_* %s" %(get_value(hotpotato, 'directory'))
    try_cmd(cmd)

    return hotpotato
