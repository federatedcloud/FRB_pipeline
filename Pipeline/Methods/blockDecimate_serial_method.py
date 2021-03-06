from method import *
from decimate import *
import os
import numpy as np
import sys

# Run Smoothing and Decimation on all blocks of data in 'split_dir'
'''
Required parameters in config file:
    split_dir, dec_name, tsamp, vsamp, do_avg, do_smooth, do_decimate,
    t_width, v_width, t_sigma, v_sigma
And from FITS header:
    TBIN, CHAN_BW
'''

def main(hotpotato):
    print("Running decimation and smoothing.\n")
   
    params_list= ['split_dir', 'filetype', 'dec_name', 'tsamp / tcombine', 'vsamp / vcombine', 
               'do_avg', 'do_smooth', 'do_decimate', 'dec_testing_mode', 'kernels', 
               't_width', 'v_width', 't_sigma', 'v_sigma', 'split_list']
    fits_params_list= ['TBIN', 'CHAN_BW']
    fil_params_list= ['tsamp', 'foff']
    print_params(params_list)
    print_fits_params(fits_params_list)
    print_fil_params(fil_params_list)

    # Get data file location
    split_dir= get_value(hotpotato, 'split_dir')
    filetype= get_value(hotpotato, 'filetype')
    dec_name= get_value(hotpotato, 'dec_name')

    # Set up dictionary with data-related parameters
    gd = {}
    if filetype == 'psrfits':
        dt= get_value(hotpotato, 'TBIN')
        dv= abs(get_value(hotpotato, 'CHAN_BW'))
        gd['tsamp'] = get_value(hotpotato, 'tsamp')
        gd['vsamp'] = get_value(hotpotato, 'vsamp')
    elif filetype == 'filterbank':
        dt= get_value(hotpotato, 'tsamp')
        dv= abs(get_value(hotpotato, 'foff'))
        # Note the naming convention change:
        gd['tsamp'] = get_value(hotpotato, 'tcombine')
        gd['vsamp'] = get_value(hotpotato, 'vcombine')
    else:
        print('Filetype not recognized. Quitting... ')
        sys.exit()

    gd['dt'] = dt
    gd['dv'] = dv

    # Set up smoothing/decimation parameters
    sd = {} 
    do_avg = get_value(hotpotato, 'do_avg')
    do_smooth = get_value(hotpotato, 'do_smooth')
    do_decimate = get_value(hotpotato, 'do_decimate')
    testing_mode= get_value(hotpotato, 'dec_testing_mode')

    if do_avg and do_decimate:
        print("Cannot block average AND decimate data. Select at most one of 'do_avg' "\
              " or 'do_decimate'")
        raise ValueError("Cannot do block averaging AND decimation. "\
                         "Select either 'do_avg' or 'do_decimate.")

    # kernel options: gaussian2d, gaussianT, gaussianV, block2d, blockT, blockV, custom
    sd['kernels'] = get_value(hotpotato, 'kernels').split(',')
    print('Smoothing kernels: %s\n' %(sd['kernels']))
    if do_avg == True:
        sd['T_width'] = int(get_value(hotpotato, 't_width') / (dt*gd['tsamp']))
        sd['V_width'] = int(get_value(hotpotato, 'v_width') / (dv*gd['vsamp']))
        sd['T_sigma'] = float(get_value(hotpotato, 't_sigma') / (dt*gd['tsamp']))
        sd['V_sigma'] = float(get_value(hotpotato, 'v_sigma') / (dv*gd['vsamp']))
    if do_decimate == True:
        sd['T_width'] = int(get_value(hotpotato, 't_width') / dt)
        sd['V_width'] = int(get_value(hotpotato, 'v_width') / dv)
        sd['T_sigma'] = float(get_value(hotpotato, 't_sigma') / dt)
        sd['V_sigma'] = float(get_value(hotpotato, 'v_sigma') / dv) 


    block_list= get_value(hotpotato, 'split_list')
    if block_list == '':
        # Get list of data files
        block_list= os.listdir(split_dir)

        files_len= len(block_list) # this is dynamic
        n= 0
        while n < files_len:
            block= block_list[n]
            if block[0:5] != 'block':
                block_list.remove(block)
                files_len-= 1 
            else:
                n+= 1
        print(block_list)
    else:
        pass

    print(block_list)
    dec_block_list= []
    for block_name in block_list:
        print(block_name)
        print(split_dir + '/' + block_name)
        print('%s/%s' %(split_dir, block_name))
        try:
            data= np.load('%s/%s' %(split_dir, block_name))
        except:
            print('The file -- %s -- does not exist in directory -- %s' %(block_name, split_dir))
            continue
        print('Data Shape: ' + str(data.shape))
        dec_data= decimate_and_smooth(gd, sd, data, do_avg, do_smooth, do_decimate, testing_mode)
        dec_data_name= dec_name + '_' + block_name
        np.save(dec_data_name, dec_data)
        dec_block_list.append(dec_data_name)

    cmd= 'mv %s* %s' %(dec_name, split_dir)
    try_cmd(cmd)    
    print("Finished decimating blocked data.\n\n")

    hotpotato['dec_block_list']= dec_block_list
    return hotpotato
