from method import *
from friends import *
import numpy as np

def main(d):
    print("Running Friend-Of-Friends")
    
    # Set up fof-specific parameters
    try:
        dec_name= d['dec_name']
        print("Running Friend-Of-Friends on Decimated data.")
        dec_file= np.load(dec_name + '.npz')
        data= dec_file[dec_file.files[0]]
    except:
        print("Running Friend-Of-Friends NON-decimated data.")
        npz_file = np.load(d['npz_name'] + '.npz')
        data= npz_file[npz_file.files[0]]
    print('Data Shape= ' + str(data.shape))

    m1 = d['m1']
    m2 = d['m2']
    t_gap = int(d['t_gap'])
    v_gap = int(d['v_gap'])
    tstart = d['tstart']
    
    # set up dictionary of global parameters
    gd = {} 
    gd['tsamp'] = int(d['tsamp'])
    gd['vsamp'] = int(d['vsamp'])
    gd['dt'] = d['TBIN']
    gd['dv'] = abs(d['CHAN_BW']) # for some reason this was negative
    dv = gd['dv']
    gd['vlow'] = d['OBSFREQ'] - dv * d['NCHAN'] / 2.0
    gd['vhigh'] = d['OBSFREQ'] + dv * d['NCHAN'] / 2.0
    
    # Run algorithm
    fof(gd, data, m1, m2, t_gap, v_gap, tstart)
    
    cmd= "mv *clust_* %s" %(d['directory'])
    try_cmd(cmd)

    return d
