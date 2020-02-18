import numpy as np

# Obtain median noisy bandpass shape.
'''
Inputs:
raw_ds = Input dynamic spectrum, 2D array, axes = [Frequency, Time]
'''
def calc_median_bandpass(raw_ds):
    bandpass = np.zeros(len(raw_ds))
    for i in range(len(bandpass)):
        bandpass[i] = np.nanmedian(raw_ds[i])
    print('Median bandpass shape calculated.')
    return bandpass
############################################################################
# Correct data for bandpass shape.
'''
Inputs:
raw_ds = Input dynamic spectrum, 2D array, axes = [Frequency, Time]
bandpass = 1D array of bandpass fluxes
'''
def correct_bandpass(raw_ds,bandpass):
    ds_bp_corrected = raw_ds/bandpass[:,None] - 1
    print('Bandpass shape removed from data.')
    return ds_bp_corrected
############################################################################
