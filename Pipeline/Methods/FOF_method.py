import sys
sys.path.insert(0, '../Modules')
from method import *
from friends import *


def main(d):
    print("Running Friend-Of-Friends")
    
    # TODO: do conversion in readconfig?
    
    # Set up fof inputs
    np_data = d['np_data'] 
    m1 = float(d['m1'])
    m2 = float(d['m2'])
    t_gap = int(d['t_gap'])
    v_gap = int(d['v_gap'])
    tstart = float(d['tstart'])
    
    # global dictionary
    gd = {}
    gd['tsamp'] = int(d['tsamp'])
    gd['vsamp'] = int(d['vsamp'])
    #dt = float(d['TBIN'])
    gd['dt'] = float(d['TBIN'])
    #dv = float(d['CHAN_BW'])
    dv = abs(float(d['CHAN_BW'])) # for some reason this was negative.
    gd['dv'] = dv
    #vlow = float(d['OBSFREQ']) - dv * float(d['NCHAN']) / 2.0
    #vhigh = float(d['OBSFREQ']) + dv * float(d['NCHAN']) / 2.0
    gd['vlow'] = float(d['OBSFREQ']) - dv * float(d['NCHAN']) / 2.0
    gd['vhigh'] = float(d['OBSFREQ']) + dv * float(d['NCHAN']) / 2.0
    
    # Run algorithm
    fof(gd, np_data, m1, m2, t_gap, v_gap, tstart)
    
    return d
