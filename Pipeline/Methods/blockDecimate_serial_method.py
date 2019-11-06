from method import *
import numpy as np

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
   
    params_list= ['split_dir', 'dec_name', 'tsamp', 'vsamp', 
               'do_avg', 'do_smooth', 'do_decimate', 'dec_testing_mode', 'kernels', 
               't_width', 'v_width', 't_sigma', 'v_sigma']
    fits_params_list= ['TBIN', 'CHAN_BW']
    print_params(params_list)
    print_fits_params(fits_params_list)
 
    # Get data file location
    split_dir= get_value(hotpotato, 'split_dir')
    dec_name= get_value(hotpotato, 'dec_name')

    # Set up dictionary with data-related parameters
    gd = {}
    dt = get_value(hotpotato, 'TBIN')
    dv = abs(get_value(hotpotato, 'CHAN_BW'))
    gd['dt'] = dt
    gd['dv'] = dv
    gd['tsamp'] = get_value(hotpotato, 'tsamp')
    gd['vsamp'] = get_value(hotpotato, 'vsamp')

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

    return hotpotato
