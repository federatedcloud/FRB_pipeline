
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid
import prepare
from matplotlib import transforms
from matplotlib import ticker

kdm= 4148.808 # MHz^2 / (pc cm^-3)
dt= 6.54761904761905e-05
dv= -.336
f0= 1375.432

# make fancy plot of 
#   (1) Dynamic spectrum (f vs. t)
#   (2) Dedispersed time series (SNR vs. t)
#   (3) Dedispersed spectrum (f vs. SNR)
#   (4) Mod Index vs. SNR


@ticker.FuncFormatter
def x_formatter(x, pos):
    loc = x * dt * 1000
    return "%.2f" % loc

@ticker.FuncFormatter
def y_formatter(y, pos):
    loc = (y * dv) + f0
    return "%.2f" % loc

def setup1(ax):
    ax.yaxis.set_label_position("right")
    ax.xaxis.set_label_position("top")
    ax.set_xlabel("Mod Index")
    ax.set_ylabel("", rotation=270, labelpad=12)
    ax.tick_params(direction='in', color='r', bottom=True, top=True, left=True, right=True, labelsize=8)
    
def setup2(ax):
    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.xaxis.set_label_position("top")
    ax.set_xlabel("De-dispersed Time Series")    
    ax.set_ylabel("")
    ax.tick_params(direction='in', color='r', bottom=True, top=True, left=True, right=True, labelbottom='off')
    ax.xaxis.set_major_formatter(x_formatter)

def setup3(ax):
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Frequency (MHz)")
    ax.tick_params(direction='in', color='r', bottom=True, top=True, left=True, right=True)
    ax.xaxis.set_major_formatter(x_formatter)
    ax.yaxis.set_major_formatter(y_formatter)

def setup4(ax):
    ax.yaxis.set_label_position("right")
    ax.set_xlabel("")
    ax.set_ylabel("De-dispersed Spectrum", rotation=270, labelpad=12)
    ax.tick_params(direction='in', color='r', bottom=True, top=True, left=True, right=True, labelleft='off')
    ax.yaxis.set_major_formatter(y_formatter)

def make_fancy_plot(data, time_series, spectrum):
    
    # data -- dynamic spectrum array

    (vchan,tchan) = data.shape
    #plt.subplots(nrows=2, ncols=1, sharex=)
   
    fig = plt.figure() 
    p = grid.GridSpec(nrows=3, ncols=3, hspace=0.04, wspace=0.04)

    #ax1 = fig.add_subplot(p[0,2])
    #setup1(ax1)
    inner_grid = grid.GridSpecFromSubplotSpec(6, 6, subplot_spec=p[0,2], wspace=0.0, hspace=0.0)
    ax1 = fig.add_subplot(inner_grid[0:5,1:6])
    setup1(ax1)

    ax3 = fig.add_subplot(p[1:3,0:2])
    setup3(ax3)
    ax3.imshow(data, origin="lower", aspect="auto", interpolation="nearest")
    
    (l,r) = ax3.get_xlim()
    (b,t) = ax3.get_ylim()
    ax3.set_xlim((l,r))
    ax3.set_ylim((b,t))    

    ax2 = fig.add_subplot(p[0,0:2], sharex= ax3)
    setup2(ax2)
    ax2.plot(time_series, linewidth=0.6, color='k')
    ax2.set_xlim((l,r))

    ax4 = fig.add_subplot(p[1:3,2], sharey= ax3)
    setup4(ax4)   
    base = plt.gca().transData
    rot = transforms.Affine2D().rotate_deg(90)    
    ax4.plot(spectrum, transform= rot + base, linewidth=0.6, color='k')
    ax4.set_ylim((b,t))

    #p.tight_layout(fig)
    plt.show()

def main():

    #ds = np.load("burst.npy")
    ds = np.random.rand(200,240)
    time_series = prepare.get_time_series(ds)
    spectrum = prepare.get_spectrum(ds)
    
    make_fancy_plot(ds, time_series, spectrum)



# prepare a dynamic spectrum for fancy plotting
# you can average across time/frequency bins using tbin/vbin

def get_axis(ds, axis, dt, dv, tbin=1, vbin=1):
    ''' Get a 1d array of times/freqs, where the data is averaged over every
        tbin/vbin bins on the time/frequency axes respectively
        <axis> should be set to "time" or "frequency"
    
        ds: data array
        axis: project data onto this axis, either 'time' or 'frequency'
        dt: size of time bins
        dv: size of freq bins
    '''    
    [vchan,tchan] = ds.shape
    if axis == "time":
        N_tbins = tchan / tbin
        times = np.zeros([N_tbins,1])
        for j in range(N_tbins):
            times[j] = dt * tbin * j
        return times

    elif axis == "frequency":
        N_vbins = vchan / vbin
        freqs = np.zeros([N_vbins,1])
        for j in range(N_vbins):
            freqs[j] = dv * vbin * j
        return freqs
    
    else:
        print("Incorrect value for <axis>. Must be either 'time' or 'frequency'")
        return


def dedisperse(ds, freqs, t0, tstart, tread, dt, DM):
    # kdm is the dispersion constant, defined at top of file
    print("Dedispersing dynamic spectrum...")
    [vchan,tchan] = ds.shape
    f0 = freqs[0]
        
    N_timebins = int(tread / dt)
    startbin = int((tstart-t0) / dt)
    ds_dd = np.zeros((vchan, N_timebins))

    print("Computing Dedispersion delays...")
    for k in range(vchan):
        # compute dispersive delay
        t_delay = DM * kdm * ((freqs[k])**(-2) - f0**(-2))
        delta_tbins = int(t_delay / dt)
        dd_startbin = startbin + delta_tbins
        #print('t_delay= ' + str(t_delay))
        #print('delta_tbins= ' + str(delta_tbins))
        #print('dd_startbin= ' + str(dd_startbin))
        if dd_startbin + N_timebins < tchan:
            ds_dd[k,:] = ds[k, dd_startbin:dd_startbin+N_timebins]
        else:
            print('Input Array does not cover enough time to conduct dedispersion.')
            print('Dedispersion Failed.')            

    return ds_dd

def get_time_series(ds):    
    # get the time series of a dynamic spectrum <ds>
    [vchan,tchan] = ds.shape

    time_series = np.zeros([tchan,1])

    for j in range(tchan):
        sum = 0
        for k in range(vchan):
            sum = sum + ds[k,j]    
        time_series[j] = sum

    return time_series

def get_spectrum(ds):
    # get the spectrum of a dynamic spectrum <ds>
    [vchan,tchan] = ds.shape
    spectrum = np.zeros([vchan,1])
    
    for k in range(vchan):
        sum = 0
        for j in range(tchan):
            sum = sum + ds[k,j]
        spectrum[k] = sum

    return spectrum
