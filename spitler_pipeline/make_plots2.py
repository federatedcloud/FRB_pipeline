
# Contains plotting function "make_avg_plot", used to create plots
# of particular regions of a dynamic spectra. In the pipeline, these regions 
# are determined by selecting candidates with the lowest modulation indices

# "plot_fil_dspec" and "plot_fil_dspec_classic" are plotting functions
# from Pete's "make_plots.py". I left them in here


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

# Read data from a fits file to a numpy array
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

# Plot some specified region of a dynamic spectrum
def make_avg_plot(filfile, work_dir, mode, color, tstart, tread, dt, freqs,  
                  avg_chan=1, avg_samp=1, dm0=0, **plt_kwargs):
    
    # MAKE SURE MODE AND COLOR PARAMETERS ARE OK
    if mode not in ["save","show"]:
        print "Invalid <mode> variable. <mode> must be 'save' or 'show'\nExiting..."
        return
    if color not in ["gray","reverse_gray","color"]:
        print "Invalid <color> setting. Must be 'gray', 'reverse_gray', or 'color'.\nExiting..."
        return

    # READ IN DATA FROM FILFILE
    nchan = len(freqs)
    tt, dd = read_fil(filfile, tstart, tread, dt, nchan)

    # AVG DATA
    favg, davg = dedisp.dspec_avg_tf_dm(dd, freqs, freqs[-1], dt, 
                        avg_chan=avg_chan, avg_samp=avg_samp, dm0=dm0)
    
    # MAKE PLOT
    ext = [tt[0], tt[-1], favg[0], favg[-1]]
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    if color == "color":
        plt.imshow(davg, aspect='auto', interpolation='nearest', 
                   origin='lower', extent=ext, **plt_kwargs)
    elif color == "gray":
        plt.imshow(davg, aspect='auto', interpolation='nearest',
                   origin='lower', extent=ext, cmap='gray', **plt_kwargs)    
    elif color == "reverse_gray":
        plt.imshow(davg, aspect='auto', interpolation='nearest',
                   origin='lower', extent=ext, cmap='gray_r', **plt_kwargs)    

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (MHz)")
    
    plt.colorbar()
    # Show or Save the plot, depending on the mode given
    if mode == "show":
        plt.show()
    if mode == "save":
        plt.savefig(work_dir + "tstart=" + str(tstart) + ".png")

    return 


