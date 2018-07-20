from method import *

import sys
sys.path.insert(0, '../FOF')
from friends import *


def main(d):
    print("Running Friend-Of-Friends")
    
    # Fix strings
    # TODO: do this better later
    
    # Set up fof inputs
    np_data = d['np_data'] 
    m1 = float(fix_str(d['m1']))
    m2 = float(fix_str(d['m2']))
    tsamp = int(fix_str(d['tsamp']))
    vsamp = int(fix_str(d['vsamp']))
    t_gap = int(fix_str(d['t_gap']))
    v_gap = int(fix_str(d['v_gap']))
    tstart = float(fix_str(d['tstart']))
    #dt = float(fix_str(d['TBIN']))
    dt = float(d['TBIN'])
    #dv = float(fix_str(d['CHAN_BW']))
    dv = float(d['CHAN_BW'])
    #vlow = float(fix_str(d['OBSFREQ'])) - dv * float(fix_str(d['NCHAN'])) / 2.0
    #vhigh = float(fix_str(d['OBSFREQ'])) + dv * float(fix_str(d['NCHAN'])) / 2.0
    vlow = float(d['OBSFREQ']) - dv * float(d['NCHAN']) / 2.0
    vhigh = float(d['OBSFREQ']) + dv * float(d['NCHAN']) / 2.0
    
    # run algorithm
    fof(np_data, m1, m2, tsamp, vsamp, t_gap, v_gap, tstart, dt, dv, vlow, vhigh)
    
    return d


def fix_str(input):
    return input.split(";")[0]
