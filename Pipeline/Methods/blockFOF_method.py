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

def main(hotpotato):
    print("Running Friend-Of-Friends.\n")

    params_list= ['split_dir', 'm1', 'm2', 't_gap', 'v_gap', 'tstart', 'fof_testing_mode', 
               'tsamp', 'vsamp', 'dec_block_list']
    fits_params_list= ['TBIN', 'CHAN_BW', 'OBSFREQ', 'NCHAN']
    print_params(params_list)
    print_fits_params(fits_params_list)
    
    # Get data file location
    split_dir= get_value(hotpotato, 'split_dir')
    dec_name= get_value(hotpotato, 'dec_name')

    # Get parameters from hotpotato
    m1 = get_value(hotpotato, 'm1')
    m2 = get_value(hotpotato, 'm2')
    t_gap = int(get_value(hotpotato, 't_gap'))
    v_gap = int(get_value(hotpotato, 'v_gap'))
    tstart = get_value(hotpotato, 'tstart')
    testing_mode= get_value(hotpotato, 'fof_testing_mode')

    # Set up dictionary of global parameters
    gd = {}
    tsamp= int(get_value(hotpotato, 'tsamp'))
    vsamp= int(get_value(hotpotato, 'vsamp'))
    gd['tsamp'] = tsamp
    gd['vsamp'] = vsamp
    gd['dt'] = get_value(hotpotato, 'TBIN')
    gd['dv'] = abs(get_value(hotpotato, 'CHAN_BW')) # for some reason this was negative
    dv = gd['dv']
    gd['vlow'] = get_value(hotpotato, 'OBSFREQ') - dv * get_value(hotpotato, 'NCHAN') / 2.0
    gd['vhigh'] = get_value(hotpotato, 'OBSFREQ') + dv * get_value(hotpotato, 'NCHAN') / 2.0

    # Get Files
    dec_block_list= get_value(hotpotato, 'dec_block_list')

    if dec_block_list == '':
        # Get list of data files
        dec_block_list= os.listdir(split_dir)
        print("Files in split_dir: " + str(dec_block_list))
    
        # Get Relevant Files
        files_len= len(dec_block_list)
        n= 0
        while n < files_len:
            block= dec_block_list[n]
            splitted= block.split('_')
            if splitted[0] != dec_name or len(splitted) < 3:
                dec_block_list.remove(block)
                files_len-= 1
            else:
                n+= 1
    else:
        pass
    print(dec_block_list)

    # Run FOF on each block
    fof_block_list= []
    for dec_block_name in dec_block_list:
        n= int(dec_block_name.split('_')[1][5:])
        print('Block: %d' %(n))
        try:
            print('%s/%s' %(split_dir, dec_block_name))
            data= np.load('%s/%s' %(split_dir, dec_block_name))
        except:
            print('The file -- %s -- does not exist in %s' %(dec_block_name, split_dir))
            continue
        print('Data Shape: ' + str(data.shape))
        if data.shape[0] > 0 and data.shape[1] > 0:
            fof(gd, data, m1, m2, t_gap, v_gap, tstart, testing_mode, True, n)
            fof_block_list.append('block%d_clust_%.1f_%d_%d_%d_%d_%d.txt' %(n, m1, m2, tsamp, vsamp, t_gap, v_gap))


    cmd= "mv *clust_* %s" %(split_dir)
    try_cmd(cmd)
    
    hotpotato['fof_block_list']= fof_block_list
    return hotpotato
