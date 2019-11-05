from method import *
from fancy_plot import *
import numpy as np

# Required parameters to put in the configuration file are:
#    ds_name, tstart, t0, tread, tsamp, vsamp, dm
# Note: other parameters are obtained from header files (stored in hotpotato)

def main(hotpotato):
    print("Making Plots.")

    ds_name = get_value(hotpotato, 'ds_name')             # file location
    tstart = get_value(hotpotato, 'tstart')
    t0 = get_value(hotpotato, 't0')
    tread = get_value(hotpotato, 'tread')
    dt = get_value(hotpotato, 'TBIN'] * get_value(hotpotato, 'tsamp')
    dv = get_value(hotpotato, 'CHAN_BW') * get_value(hotpotato, 'vsamp')
    nsub = get_value(hotpotato, 'NCHAN') * get_value(hotpotato, 'vsamp')
    vmax = get_value(hotpotato, 'OBSFREQ')
    dm = get_value(hotpotato, 'dm')
    
    freqs = vmax + np.arange(nsub) * dv
    
    ds_file = np.load(ds_name + '.npz')
    ds = np.flip(ds_file[ds_file.files[0]], 0)
    ds_dd = dedisperse(ds, freqs, t0, tstart, tread, dt, dm)
    time_series = get_time_series(ds_dd)
    spectrum = get_spectrum(ds_dd)
    
    make_fancy_plot(ds[:,:time_series.size], time_series, spectrum)

    return hotpotato
