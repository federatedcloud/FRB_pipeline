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
    t_gap = int(fix_str(d['t_gap']))
    v_gap = int(fix_str(d['v_gap']))
    tstart = float(fix_str(d['tstart']))
    
    gd = {}
    gd['tsamp'] = int(fix_str(d['tsamp']))
    gd['vsamp'] = int(fix_str(d['vsamp']))
    #dt = float(fix_str(d['TBIN']))
    gd['dt'] = float(d['TBIN'])
    #dv = float(fix_str(d['CHAN_BW']))
    dv = abs(float(d['CHAN_BW'])) # for some reason this was negative.
    gd['dv'] = dv
    #vlow = float(fix_str(d['OBSFREQ'])) - dv * float(fix_str(d['NCHAN'])) / 2.0
    #vhigh = float(fix_str(d['OBSFREQ'])) + dv * float(fix_str(d['NCHAN'])) / 2.0
    gd['vlow'] = float(d['OBSFREQ']) - dv * float(d['NCHAN']) / 2.0
    gd['vhigh'] = float(d['OBSFREQ']) + dv * float(d['NCHAN']) / 2.0
    # run algorithm
    fof(gd, np_data, m1, m2, t_gap, v_gap, tstart)
    
    return d


def fix_str(input):
    return input.split(";")[0]
