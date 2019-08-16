from method import *
from decimate import *
import os
import numpy as np

# Run Smoothing and Decimation on all blocks of data in 'split_dir'
'''
Required parameters in config file:
    split_dir, dec_name, tsamp, vsamp, do_avg, do_smooth, do_decimate,
    t_width, v_width, t_sigma, v_sigma
And from FITS header:
    TBIN, CHAN_BW
'''

def main(d):
    print("Running decimation and smoothing.")
    
    # Get data file location
    split_dir= d['split_dir']
    dec_name= d['dec_name']

    # Set up dictionary with data-related parameters
    gd = {}
    dt = d['TBIN']
    dv = abs(d['CHAN_BW'])
    gd['dt'] = dt
    gd['dv'] = dv
    gd['tsamp'] = d['tsamp']
    gd['vsamp'] = d['vsamp']

    # Set up smoothing/decimation parameters
    sd = {} 
    do_avg = d['do_avg']
    do_smooth =d['do_smooth']
    do_decimate = d['do_decimate']
    testing_mode= d['dec_testing_mode']

    if do_avg and do_decimate:
        print("Cannot block average AND decimate data. Select at most one of 'do_avg' "\
              " or 'do_decimate'")
        raise ValueError("Cannot do block averaging AND decimation. "\
                         "Select either 'do_avg' or 'do_decimate.")

    # kernel options: gaussian2d, gaussianT, gaussianV, block2d, blockT, blockV, custom
    sd['kernels'] = d['kernels'].split(',')
    print('Smoothing kernels: %s\n' %(sd['kernels']))
    if do_avg == True:
        sd['T_width'] = int(d['t_width'] / (dt*gd['tsamp']))
        sd['V_width'] = int(d['v_width'] / (dv*gd['vsamp']))
        sd['T_sigma'] = float(d['t_sigma'] / (dt*gd['tsamp']))
        sd['V_sigma'] = float(d['v_sigma'] / (dv*gd['vsamp']))
    if do_decimate == True:
        sd['T_width'] = int(d['t_width'] / dt)
        sd['V_width'] = int(d['v_width'] / dv)
        sd['T_sigma'] = float(d['t_sigma'] / dt)
        sd['V_sigma'] = float(d['v_sigma'] / dv) 

    # Get list of data files
    files= os.listdir(split_dir)

    files_dict= {}
    files_len= len(files) # this is dynamic
    n= 0
    while n < files_len:
        print(n)
        block= files[n]
        if block.split('_')[0] != 'block':
            files.remove(block)
            files_len-= 1 
        else:
            files_dict[int(block.split('_')[1])]= block
            n+= 1
    
    # Sort the blocks
    sorted_files= []
    for n in range(len(files)):
        sorted_files.append(files_dict[n])
    print("Files: " +str(files))
    print("Sorted Files: " + str(sorted_files))
    
    files= sorted_files
    del sorted_files

    # Run smoothing and decimation on all blocks of data
    for block in files:
        n= block.split('_')[1]
        print('Block: %s' %(n))
        data= np.load('%s/%s' %(split_dir, block))
        print('Data Shape: ' + str(data.shape))
        dec_data= decimate_and_smooth(gd, sd, data, do_avg, do_smooth, do_decimate, testing_mode)
        np.save(dec_name + '_' + block, dec_data)

    cmd= 'mv %s* %s' %(dec_name, split_dir)
    try_cmd(cmd)    
    print("Finished decimating blocked data.\n\n")

    return d
