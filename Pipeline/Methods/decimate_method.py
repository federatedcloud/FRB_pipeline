from method import *
from decimate import *

# Required parameters to put in the configuration file are:
#    dec_name, do_avg, do_smooth, do_decimate, t_width, v_width, t_sigma, v_sigma, tsamp, vsamp
# Optional parameters:
#    kernels
# Note: other parameters are obtained from header files (stored in hotpotato)

def main(hotpotato):
    print("Running decimation and smoothing.")
    # Set up dictionary with data-related parameters
    dec_name = get_value(hotpotato, 'dec_name')
    gd = {}
    dt = float(get_value(hotpotato, 'TBIN'))
    dv = abs(float(get_value(hotpotato, 'CHAN_BW')))
    gd['dt'] = dt
    gd['dv'] = dv
    gd['tsamp'] = int(get_value(hotpotato, 'tsamp'))
    gd['vsamp'] = int(get_value(hotpotato, 'vsamp'))

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
    npzfile= np.load(get_value(hotpotato, 'npz_name') + '.npz')
    print(npzfile)
    print(npzfile.files)
    dec_data= decimate_and_smooth(gd, sd, npzfile[npzfile.files[0]], do_avg, do_smooth, do_decimate, testing_mode)
    np.savez(dec_name, dec_data)
    return hotpotato

