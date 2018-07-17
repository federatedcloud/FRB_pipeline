'''Note: Not finished. Still need to implement
   plot (4), and compute SNRs for (2) and (3). 
   Currently, just the signal is plotted, not SNR.
   Also the x-axis for the spectrum is messed up.
'''

# Standard Imports:
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid
from matplotlib import transforms
from matplotlib import ticker

# Local Imports:
import make_plots
import params
import simple_dm
import friends

# make connected plot of 
#   (1) Dynamic spectrum (f vs. t)
#   (2) Dedispersed time series (SNR vs. t)
#   (3) Dedispersed spectrum (f vs. SNR)
#   (4) Mod Index vs. SNR

# From params
dt = params.dt
dv = params.dv
filfile = params.filfile # masked raw data file
dt = params.dt
nsub = params.nsub
freqs = params.freqs
avg_samp = params.avg_samp
avg_chan = params.avg_chan

# ranges of SNR:
spectrum_SNR = ()
time_series_SNR = ()

# Formatters for X and Y axes of dynamic spectrum
@ticker.FuncFormatter
def x_formatter(x, pos):
    loc = x * dt * avg_samp
    return "%.1f" % loc

@ticker.FuncFormatter
def y_formatter(y, pos):
    loc = (y * avg_chan * dv) + freqs[0]
    return "%.1f" % loc

xlocator = ticker.MultipleLocator(0.1 / (dt * avg_samp))
ylocator = ticker.MultipleLocator(50.0 / (dv * avg_chan))

# Functions to format the four plots
def setup1(ax):
    ax.yaxis.set_label_position("right")
    ax.xaxis.set_label_position("top")
    ax.set_xlabel("Mod Index")
    ax.set_ylabel("SNR", rotation=270, labelpad=12)
    ax.tick_params(direction='in', color='r', bottom=True, top=True, left=True, right=True, labelsize=8)
    
def setup2(ax):
    ax.xaxis.set_label_position("top")
    ax.set_xlabel("De-dispersed Time Series")    
    ax.set_ylabel("SNR")
    ax.tick_params(direction='in', color='r', bottom=True, top=True, left=True, right=True, labelbottom='off')
    ax.xaxis.set_major_formatter(x_formatter)

def setup3(ax):
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (MHz)")
    ax.tick_params(direction='in', color='r', bottom=True, top=True, left=True, right=True)
    ax.xaxis.set_major_formatter(x_formatter)
    ax.yaxis.set_major_formatter(y_formatter)
    ax.xaxis.set_major_locator(xlocator)
    ax.yaxis.set_major_locator(ylocator)

def setup4(ax):
    ax.yaxis.set_label_position("right")
    ax.set_xlabel("SNR")
    ax.set_ylabel("De-dispersed Spectrum", rotation=270, labelpad=12)
    ax.tick_params(direction='in', color='r', bottom=True, top=True, left=True, right=True, labelleft='off')
    ax.yaxis.set_major_formatter(y_formatter)

# Main Function -- make the plots
def make_fancy_plot(tstart, tread, dm):   
 
    print "Reading masked data into array..."
    (times, data) = make_plots.read_fil(filfile, tstart, tread, dt, nsub) 
    print type(times)
    print times.shape
    print type(data)
    print data.shape
    for j in range(data.shape[0]):
        print data[j,:]
    plt.imshow(data)
    plt.show()
         
    print "Averaging masked data..."
    data_avgT = friends.avg_time(data, avg_samp)
    data_avgTV = friends.avg_freq(data_avgT, avg_chan)
   
    #plt.imshow(data_avgTV)
    #plt.show()
   
    print "Dedispersing and averaging masked data..." 
    DD = simple_dm.dedisperse_dspec(data, dm, freqs, freqs[-1], dt)
    DD_avgT = friends.avg_time(DD, avg_samp)
    DD_avgTV = friends.avg_freq(DD_avgT, avg_chan)    

    #plt.imshow(DD_avgTV)
    #plt.show()
 
    (vchan,tchan) = data.shape
    if vchan != nsub:
        print "something strange is happening with the frequency channels"

    print "Computing spectrum..."
    spectrum = friends.avg_time(data_avgTV, data_avgTV.shape[1])
    #plt.plot(spectrum)
    #plt.show()

    print "Computing time series..."
    time_series = friends.avg_freq(DD_avgTV, DD_avgTV.shape[0])
    #plt.plot(np.arange(time_series.size),time_series[0,:])
    #plt.show()


    fig = plt.figure() 
    p = grid.GridSpec(nrows=3, ncols=3, hspace=0.04, wspace=0.04)

    # Plot (1)
    inner_grid = grid.GridSpecFromSubplotSpec(6, 6, subplot_spec=p[0,2], wspace=0.0, hspace=0.0)
    ax1 = fig.add_subplot(inner_grid[0:5,1:6])
    setup1(ax1)

    # Plot (3)
    ax3 = fig.add_subplot(p[1:3,0:2])
    setup3(ax3)
    ax3.imshow(data_avgTV, origin="lower", cmap="gray", aspect="auto", interpolation="nearest")
    
    (l,r) = ax3.get_xlim()
    (b,t) = ax3.get_ylim()
    ax3.set_xlim((l,r))
    ax3.set_ylim((b,t))    

    # Plot (2)
    ax2 = fig.add_subplot(p[0,0:2], sharex= ax3)
    setup2(ax2)
    ax2.plot(time_series[0,:], linewidth=0.6, color='k')
    ax2.set_xlim((l,r))

    # Plot (4)
    ax4 = fig.add_subplot(p[1:3,2], sharey= ax3)
    setup4(ax4)   
    base = plt.gca().transData
    rot = transforms.Affine2D().rotate_deg(90)    
    ax4.plot(spectrum, transform= rot + base, linewidth=0.6, color='k')
    ax4.set_ylim((b,t))

    plt.show()

def main():

    make_fancy_plot(128.0,0.5,560.0)


if __name__ == "__main__":
    main()

