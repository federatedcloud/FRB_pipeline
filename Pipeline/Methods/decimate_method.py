from method import *
from decimate import *

# Required parameters to put in the configuration file are:
#    dec_name, do_avg, do_smooth, do_decimate, t_width, v_width, t_sigma, v_sigma, tsamp, vsamp
# Optional parameters:
#    kernels
# Note: other parameters are obtained from header files (stored in hotpotato)

def main(hotpotato):
    print("Running decimation and smoothing.\n")

    params_list= ['dec_name', 'tsamp', 'vsamp', 'do_avg', 'do_smooth', 
               'do_decimate', 'dec_testing_mode', 't_width', 'v_width', 't_sigma', 
               'v_sigma', 'kernels', 'npz_name']
    fits_params_list= ['TBIN', 'CHAN_BW']
    print_params(params_list)
    print_fits_params(fits_params_list)

    # Set up dictionary with data-related parameters
    split_dir= get_value(hotpotato, 'split_dir')
    filetype= get_value(hotpotato, 'filetype')
    dec_name= get_value(hotpotato, 'dec_name')

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
    do_avg = bool(int(get_value(hotpotato, 'do_avg')))
    do_smooth = bool(int(get_value(hotpotato, 'do_smooth')))
    do_decimate = bool(int(get_value(hotpotato, 'do_decimate')))
    testing_mode = get_value(hotpotato, 'dec_testing_mode')

    if do_avg and do_decimate:
        print("Cannot block average AND decimate data. Select at most one of 'do_avg' "\
              " or 'do_decimate'")
        raise ValueError("Cannot do block averaging AND decimation. "\
                         "Select either 'do_avg' or 'do_decimate.")

    # kernel options: gaussian2d, gaussianT, gaussianV, block2d, blockT, blockV, custom
    sd['kernels'] = get_value(hotpotato, 'kernels').split(',')
    print(sd['kernels'])
    if do_avg == True:
        sd['T_width'] = int(float(get_value(hotpotato, 't_width')) / (dt*gd['tsamp']))
        sd['V_width'] = int(float(get_value(hotpotato, 'v_width')) / (dv*gd['vsamp']))
        sd['T_sigma'] = float(float(get_value(hotpotato, 't_sigma')) / (dt*gd['tsamp']))
        sd['V_sigma'] = float(float(get_value(hotpotato, 'v_sigma')) / (dv*gd['vsamp']))
    if do_decimate == True:
        sd['T_width'] = int(float(get_value(hotpotato, 't_width')) / dt)
        sd['V_width'] = int(float(get_value(hotpotato, 'v_width')) / dv)
        sd['T_sigma'] = float(float(get_value(hotpotato, 't_sigma')) / dt)
        sd['V_sigma'] = float(float(get_value(hotpotato, 'v_sigma')) / dv) 

    # Run decimation and smoothing
    npzfile= np.load(get_value(hotpotato, 'npz_name') + '.npz', allow_pickle=True)
    dec_data= decimate_and_smooth(gd, sd, npzfile[npzfile.files[0]], do_avg, do_smooth, do_decimate, testing_mode)
    np.save(dec_name, dec_data)
    return hotpotato

