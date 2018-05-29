import numpy as np
import matplotlib.pyplot as plt
import os
import simple_dm as dedisp

import params

def plot_fil_dspec(filfile, n=8, nsblk=15270, nchan=960):
    """
    filfile = raw_data_with_mask.fits file
    
    n = number of subints to plot
    nsblk = number of spectra per subint
    nchan = number of channels 
    """
    vals = n * nsblk * nchan
    dat = np.fromfile(filfile, dtype='float32', count=vals)
    dat = np.reshape(dat, (-1, nchan))

    cmap = plt.cm.get_cmap('tab10', 10)
    ext = [0, nchan, 0, int(len(dat)/nsblk)]
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.imshow(dat, interpolation='nearest', aspect='auto', 
              origin='lower', extent=ext, vmin=0, vmax=9, cmap=cmap)
    
    plt.colorbar()

    ax.set_xlabel("Frequency Channels")
    ax.set_ylabel("Subint Number")
    plt.show()
    return 


def plot_fil_dspec_classic(filfile, n=8, nsblk=15270, nchan=960):
    """
    filfile = raw_data_with_mask.fits file
    
    n = number of subints to plot
    nsblk = number of spectra per subint
    nchan = number of channels 
    """
    vals = n * nsblk * nchan
    dat = np.fromfile(filfile, dtype='float32', count=vals)
    dat = np.reshape(dat, (-1, nchan))

    cmap = plt.cm.viridis
    ext = [0, nchan, 0, int(len(dat)/nsblk)]
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.imshow(dat, interpolation='nearest', aspect='auto', 
              origin='lower', extent=ext, cmap=cmap)
    
    plt.colorbar()

    ax.set_xlabel("Frequency Channels")
    ax.set_ylabel("Subint Number")
    plt.show()
    return 


def read_fil(filfile, tstart, tread, dt, nchan):
    nspec_start = int(tstart / dt)
    nspec_read  = int(tread / dt)
    
    f = open(filfile, "rb")
    # 4 bytes / float
    f.seek( nspec_start * nchan * 4, os.SEEK_SET )
    
    nread = nspec_read * nchan
    dd = np.fromfile(f, dtype='float32', count=nread)
    dd = np.reshape(dd, (-1, nchan))

    tt = np.arange(len(dd)) * dt + nspec_start * dt
    return tt, dd


def make_avg_plot(filfile, tstart, tread, dt, freqs,  
                  avg_chan=1, avg_samp=1, dm0=0, **plt_kwargs):
    # READ IN DATA FROM FILFILE
    nchan = len(freqs)
    tt, dd = read_fil(filfile, tstart, tread, dt, nchan)

    # AVG DATA
    favg, davg = dedisp.dspec_avg_tf_dm(dd, freqs, freqs[-1], dt, 
                        avg_chan=avg_chan, avg_samp=avg_samp, dm0=dm0)
    
    # MAKE PLOT
    ext = [favg[0], favg[-1], tt[0], tt[-1]]
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.imshow(davg, aspect='auto', interpolation='nearest', 
               origin='lower', extent=ext, **plt_kwargs)
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Time (s)")
    
    plt.colorbar()
    plt.show()
    return 



# MAKE AVG DETECT PLOT
#fildir = '/mnt/data1/make_dynamic_spectra_without_RFI/testing_datafile'
#filfile = '%s/raw_data_with_mask.fits' %fildir
#
#freqs = 1214.28955078 + np.arange(960) * 0.336182022493
#dt = 6.54761904761905E-05
#
#tstart = 128.0 # sec
#tread  = 0.5   # sec

freqs = 1214.28955078 + np.arange(params.nsub) * 0.336182022493
vmin = params.vmin
vmax = params.vmax

#make_avg_plot(params.filfile, params.tstart, params.tread, params.dt, freqs, 
#              params.avg_chan, params.avg_samp, params.dm0, 
#              vmin=6, vmax=7)
##              vmin, vmax)
