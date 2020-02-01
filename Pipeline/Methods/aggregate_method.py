from method import *
from plotify import *
import numpy as np
import os
import glob

# Combine the cluster files from a blockFOF 'split_dir'
'''
Required parameters in config file:
    split_dir, block_size, overlap, sort_stat
And from FITS header:       
    TBIN, CHAN_BW, OBSFREQ, NCHAN
'''

def main(hotpotato):
    print("Aggregating FOF results.\n")

    params_list= ['split_dir', 'block_size', 'overlap', 'sort_stat']
    fits_params_list= ['TBIN', 'CHAN_BW', 'OBSFREQ', 'NCHAN']
    print_params(params_list)
    print_fits_params(fits_params_list)
    
    block_size= get_value(hotpotato, 'block_size')
    overlap= get_value(hotpotato, 'overlap')
    sort_stat= get_value(hotpotato, 'sort_stat')

    # Get data file location
    split_dir= get_value(hotpotato, 'split_dir')

    # Get Files
    fof_block_list= get_value(hotpotato, 'fof_block_list')

    if fof_block_list == '':
        fof_block_list= os.listdir(split_dir)
        #print(fof_block_list)
    
        # Get Relevant Files
        files_len= len(fof_block_list)
        n= 0
        while n < files_len:
            block= fof_block_list[n]
            splitted= block.split('_')
            if len(splitted) < 2 or splitted[1] != 'clust' or block[:5] != 'block' or block[-4:] != '.txt':
                fof_block_list.remove(block)
                files_len-= 1
            else:
                n+= 1
        #print(fof_block_list)
    else:
        pass

    aggregate_results(split_dir, fof_block_list, sort_stat, block_size, overlap)

    return hotpotato
