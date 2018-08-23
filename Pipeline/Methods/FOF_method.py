import sys
sys.path.insert(0, '../Modules')
from method import *
from friends import *


def main(d):
    print("Running Friend-Of-Friends")
    
    # Set up fof inputs
    np_data = d['np_data']
    m1 = d['m1']
    m2 = d['m2']
    t_gap = int(d['t_gap'])
    v_gap = int(d['v_gap'])
    tstart = d['tstart']
    
    # global dictionary
    gd = {}
    gd['tsamp'] = int(d['tsamp'])
    gd['vsamp'] = int(d['vsamp'])
    gd['dt'] = d['TBIN']
    gd['dv'] = abs(d['CHAN_BW']) # for some reason this was negative
    gd['vlow'] = d['OBSFREQ'] - dv * d['NCHAN'] / 2.0
    gd['vhigh'] = d['OBSFREQ'] + dv * d['NCHAN'] / 2.0
    
    # Run algorithm
    fof(gd, np_data, m1, m2, t_gap, v_gap, tstart)
    
    return d
