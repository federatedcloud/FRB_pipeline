from method import *

import sys
sys.path.insert(0, './Modules/')
from decimate import *

def main(d):
    print("Running decimation and smoothing.")

    # Set up dictionary with data-related parameters
    gd = {}
    dt = float(d['TBIN'])
    dv = abs(float(d['CHAN_BW']))
    gd['dt'] = dt
    gd['dv'] = dv
    gd['tsamp'] = int(d['tsamp'])
    gd['vsamp'] = int(d['vsamp'])

    # Set up smoothing/decimation parameters
    sd = {} 
    do_avg = bool(int(d['do_avg']))
    do_smooth = bool(int(d['do_smooth']))
    do_decimate = bool(int(d['do_decimate']))

    if do_avg and do_decimate:
        print("Cannot block average AND decimate data. Select at most one of 'do_avg' "\
              " or 'do_decimate'")
        raise ValueError("Cannot do block averaging AND decimation. "\
                         "Select either 'do_avg' or 'do_decimate.")

    # kernel options: gaussian2d, gaussianT, gaussianV, block2d, blockT, blockV, custom
    sd['kernels'] = d['kernels'].split(', ')

    if do_avg == True:
        sd['T_width'] = int(float(d['T_width']) / (dt*gd['tsamp']))
        sd['V_width'] = int(float(d['V_width']) / (dv*gd['vsamp']))
        sd['T_sigma'] = float(float(d['T_sigma']) / (dt*gd['tsamp']))
        sd['V_sigma'] = float(float(d['V_sigma']) / (dv*gd['vsamp']))
    if do_decimate == True:
        sd['T_width'] = int(float(d['T_width']) / dt)
        sd['V_width'] = int(float(d['V_width']) / dv)
        sd['T_sigma'] = float(float(d['T_sigma']) / dt)
        sd['V_sigma'] = float(float(d['V_sigma']) / dv) 

    # Run decimation and smoothing
    d['dec_data'] = decimate_and_smooth(gd, sd, d['np_data'], do_avg, do_smooth, do_decimate)
    return d
