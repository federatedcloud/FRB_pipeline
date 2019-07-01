from method import *
from fancy_plot import *
import numpy as np

def main(d):
    print("Making Plots.")

    ds_name= d['ds_name']             # file location
    tstart= d['tstart']
    t0= d['t0']
    tread= d['tread']
    dt= d['TBIN'] * d['tsamp']
    dv= d['CHAN_BW'] * d['vsamp']
    nsub= d['NCHAN'] * d['vsamp']
    vmax= d['OBSFREQ']
    dm= d['dm']

    freqs= vmax + np.arange(nsub) * dv
    
    ds_file= np.load(ds_name + '.npz')
    ds= np.flip(ds_file[ds_file.files[0]], 0)
    ds_dd= dedisperse(ds, freqs, t0, tstart, tread, dt, dm)
    time_series= get_time_series(ds_dd)
    spectrum= get_spectrum(ds_dd)
    
    make_fancy_plot(ds[:,:time_series.size], time_series, spectrum)

    return d
