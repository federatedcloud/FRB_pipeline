from method import *
from friends import *
import numpy as np
import os
import glob

# Run FOF algorithm on all blocks of data in 'split_dir'
'''
Required parameters in config file:
    directory, split_dir, m1, m2, t_gap, v_gap, tstart, tsamp, vsamp, fof_testing_mode
And from FITS header:       
    TBIN, CHAN_BW, OBSFREQ, NCHAN
'''

def main(d):
    print("Running Friend-Of-Friends")
    
    # Get data file location
    split_dir= d['split_dir']

    # Get parameters from hotpotato
    m1 = d['m1']
    m2 = d['m2']
    t_gap = int(d['t_gap'])
    v_gap = int(d['v_gap'])
    tstart = d['tstart']
    test_mode= d['fof_testing_mode']

    # Set up dictionary of global parameters
    gd = {} 
    gd['tsamp'] = int(d['tsamp'])
    gd['vsamp'] = int(d['vsamp'])
    gd['dt'] = d['TBIN']
    gd['dv'] = abs(d['CHAN_BW']) # for some reason this was negative
    dv = gd['dv']
    gd['vlow'] = d['OBSFREQ'] - dv * d['NCHAN'] / 2.0
    gd['vhigh'] = d['OBSFREQ'] + dv * d['NCHAN'] / 2.0
    
    # Get list of data files
    files= os.listdir(split_dir)
    print(files)
    
    # Get Relevant Files
    files_len= len(files)
    n= 0
    while n < files_len:
        block= files[n]
        splitted= block.split('_')
        if splitted[0] != 'dec' or len(splitted) < 3:
            files.remove(block)
            files_len-= 1
        else:
            n+= 1
    print(files)

    # Run friends-of-friends on all blocks of data
    for block in files:
        n= block.split('_')[3]
        print('Block: %s' %(n))
        data= np.load('%s/%s' %(split_dir, block))
        print("Data Shape: " + str(data.shape))
        if data.shape[0] > 0 and data.shape[1] > 0:
            fof(gd, data, m1, m2, t_gap, v_gap, tstart, test_mode)
    
    output_files= glob.glob('*clust_*')
    for clust_file in output_files:
        cmd= 'mv %s block%s_%s' %(clust_file, n, clust_file)
        try_cmd(cmd)


    cmd= "mv *clust_* %s" %(d['directory'])
    try_cmd(cmd)

    
    return d
