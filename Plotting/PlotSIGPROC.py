#!/usr/bin/env python
"""
Made by Shiva Lakshmanan 2018

Some code to plot SIGPROC files. SIGRPOC files do not have headers,
so these numbers are very specific to Arecibo data. However, you can change them
accordingly and the code should still work

Note: if you want to calculate time samples. You need the time sample size.
    called that x. Say you want 100s to 150s. the start time sample is
    100/x and the end time sample is 150/x. MAKE SURE TO CAST THOSE NUMBERS TO INTEGERS
    Because we need them to be indices of an array, so they must be integers. 
"""
import numpy as np
def plotSIGPROC(file_name, start_time_sample, end_time_sample, combined=True):
    freqs = 960 #hardcoded because SIGPROC files do not have headers. But freqs is the number of frequency channels. 
    if combined == False:
        freqs = 512
    dat = np.fromfile(file_name, dtype='float32', count=end_time_sample*freqs)
    dat = np.reshape(dat, (end_time_sample, freqs))
    dat = dat[start_time_sample:end_time_sample]
    dat = np.transpose(dat)
    imshow(dat, aspect='auto', interpolation='nearest', origin='lower')
    colorbar()