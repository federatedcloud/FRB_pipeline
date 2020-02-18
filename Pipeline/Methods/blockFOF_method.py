from method import *
from friends import *
import numpy as np
import os
import sys

# Run FOF algorithm on all blocks of data in 'split_dir'
'''
Required parameters in config file:
    directory, split_dir, m1, m2, t_gap, v_gap, tstart, tsamp, vsamp, fof_testing_mode
And from FITS header:       
    TBIN, CHAN_BW, OBSFREQ, NCHAN
'''

def main(hotpotato):
    print("Running Friend-Of-Friends.\n")

    params_list= ['split_dir', 'filetype', 'm1', 'm2', 't_gap', 'v_gap', 'tstart', 'fof_testing_mode', 
               'tsamp', 'vsamp', 'dec_block_list']
    fits_params_list= ['TBIN', 'CHAN_BW', 'OBSFREQ', 'NCHAN']
    fil_params_list= ['tsamp', 'foff', 'vlow', 'vhigh']
    print_params(params_list)
    print_fits_params(fits_params_list)
    print_fil_params(fil_params_list)    

    # Get data file location
    split_dir= get_value(hotpotato, 'split_dir')
    filetype= get_value(hotpotato, 'filetype')
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
        gd['vlow']= get_value(hotpotato, 'vlow')
        gd['vhigh']= get_value(hotpotato, 'vhigh')
    else:
        print('Filetype not recognized. Quitting... ')
        sys.exit()

    gd['dt']= dt
    gd['dv']= dv

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
            if get_value(hotpotato, 'bandpass_name') != '':
                clust_name= 'block%d_clust_%.1f_%d_%d_%d_%d_%d.txt' %(n, m1, m2, tcombine, vcombine, t_gap, v_gap)
                superclust_name= 'block%d_superclust_%.1f_%d_%d_%d_%d_%d.txt' %(n, m1, m2, tcombine, vcombine, t_gap, v_gap)
                png_name= 'block%d_clust_%.1f_%d_%d_%d_%d_%d.png' %(n, m1, m2, tcombine, vcombine, t_gap, v_gap)

                bandpass_str= dec_block_name[dec_block_name.find('chans'):dec_block_name.find('.npy')]
                bandpass_clust_name= 'block%d_%s_clust_%.1f_%d_%d_%d_%d_%d.txt' %(n, bandpass_str, m1, m2, tcombine, vcombine, t_gap, v_gap)
                bandpass_superclust_name= 'block%d_%s_superclust_%.1f_%d_%d_%d_%d_%d.txt' %(n, bandpass_str, m1, m2, tcombine, vcombine, t_gap, v_gap)
                bandpass_png_name= 'block%d_%s_clust_%.1f_%d_%d_%d_%d_%d.png' %(n, bandpass_str, m1, m2, tcombine, vcombine, t_gap, v_gap)
                cmd1= 'mv %s %s' %(clust_name, bandpass_clust_name)
                cmd2= 'mv %s %s' %(superclust_name, bandpass_superclust_name)
                cmd3= 'mv %s %s' %(png_name, bandpass_png_name)
                try_cmd(cmd1)
                try_cmd(cmd2)
                try_cmd(cmd3)
                fof_block_list.append(bandpass_clust_name)
            else:
                clust_name= 'block%d_clust_%.1f_%d_%d_%d_%d_%d.txt' %(n, m1, m2, tsamp, vsamp, t_gap, v_gap)
                fof_block_list.append(clust_name)


    cmd= "mv *clust_* %s" %(split_dir)
    try_cmd(cmd)
    
    hotpotato['fof_block_list']= fof_block_list
    return hotpotato
