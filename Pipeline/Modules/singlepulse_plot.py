from method import *
import bisect, os, sys, getopt, infodata, glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from scipy import *

# Candidate class for storing information about a certain pulse from its .singlepulse file
class candidate:
    def __init__(self, DM, sigma, time, bin, downfact, block, sig, mean):
        self.DM = DM
        self.sigma = sigma
        self.time = time
        self.bin = bin
        self.downfact = downfact
        self.block = block
        self.sig = sig
        self.mean = mean
    def __str__(self):
        return "%7.2f %7.2f %13.6f %10d     %3d %3d %3.2f %5.2f\n"%\
               (self.DM, self.sigma, self.time, self.bin, self.downfact, \
                  self.block, self.sig, self.mean)
    def __cmp__(self, other):
    # Sort by time (i.e. bin) by default)
        return cmp(self.bin, other.bin)

# Function that reads the singlepulse files and creates a list of candidate objects 
def read_singlepulse_files(infiles, threshold, T_start, T_end):
    info0 = None
    DMs = []
    candlist = []
    num_v_DMstr = {}
    for ii, infile in enumerate(infiles):
        if infile.endswith(".singlepulse"):
            filenmbase = infile[:infile.rfind(".singlepulse")]
        elif infile.endswith(".cluster"):
            filenmbase = infile[:infile.rfind(".cluster")]
        else:
            filenmbase = infile
        info = infodata.infodata(filenmbase+".inf")
        DMstr = "%.2f"%info.DM
        DMs.append(info.DM)
        num_v_DMstr[DMstr] = 0
        if ii==0:
            info0 = info
        if os.stat(infile)[6]:
            try:
                cands = np.loadtxt(infile)
                if len(cands.shape)==1:
                    cands = np.asarray([cands])
                for cand in cands:
                    if cand[2] < T_start: continue
                    if cand[2] > T_end: break
                    if cand[1] >= threshold:
                        if infile.endswith(".cluster"): candlist.append(clust_cand(*cand))
                        else: candlist.append(candidate(*cand))
                        num_v_DMstr[DMstr] += 1
            except:  # No candidates in the file
                IndexError
    DMs.sort()
    return info0, DMs, candlist, num_v_DMstr

def make_singlepulse_plot(sp_directory, threshold):
        """
        Creates an SNR histogram, a DM histogram, a SNR vs. DM graph, and a DM vs. time bubble
        plot with SNR as the 3rd dimension.
        Inputs:
        sp_directory = the directory where the .singlepulse files are located
        """
        args = glob.glob(sp_directory + '/*.singlepulse')
        info, DMs, candlist, num_v_DMstr = \
                      read_singlepulse_files(args, threshold, 0, 1e9)
        orig_N, orig_dt = int(info.N), info.dt
        obstime = orig_N * orig_dt

        DMs.sort()
        snrs = []
        for cand in candlist:
            snrs.append(cand.sigma)
        if snrs:
            maxsnr = max(int(max(snrs)), int(threshold)) + 3
        else:
            maxsnr = int(5.0) + 3

        num_v_DM = np.zeros(len(DMs))
        for ii, DM in enumerate(DMs):
            num_v_DM[ii] = num_v_DMstr["%.2f"%DM]
        DMs = np.asarray(DMs)


        fig = plt.figure(figsize = (15,8))
        gs = fig.add_gridspec(2,3)

        ax1 = fig.add_subplot(gs[0,0])
        ax2 = fig.add_subplot(gs[0,1])
        ax3 = fig.add_subplot(gs[0,2])
        ax4 = fig.add_subplot(gs[1,:])


        ax1.hist(snrs, int(maxsnr-threshold+1), range = (threshold, maxsnr), edgecolor = 'black', linewidth = 0.7, \
             log = True, histtype = 'step')
        ax1.set(xlabel = 'Signal-to-noise ratio', ylabel = 'Number of Pulses')
        ax1.xaxis.set_minor_locator(AutoMinorLocator())
        ax1.tick_params(axis = "both", direction = "in", which = 'both',  top = True, right = True, bottom =True)
        ax1.margins(x=0) 

        ax2.hist(DMs[:], DMs, weights = num_v_DM, edgecolor='black', linewidth = 0.7, histtype = 'step')
        ax2.set(xlabel = 'DM (cm$^{-3}$ pc)', ylabel = 'Number of Pulses')
        ax2.xaxis.set_minor_locator(AutoMinorLocator())
        ax2.yaxis.set_minor_locator(AutoMinorLocator())
        ax2.tick_params(axis = "both", direction = "in", which = 'both',  top = True, right = True)
        ax2.margins(x=0) 

        cand_ts = np.zeros(len(candlist), dtype=np.float32)
        cand_SNRs = np.zeros(len(candlist), dtype=np.float32)
        cand_DMs = np.zeros(len(candlist), dtype=np.float32)
        for ii, cand in enumerate(candlist):
            cand_ts[ii], cand_SNRs[ii], cand_DMs[ii] = \
                         cand.time, cand.sigma, cand.DM

        ax3.scatter(cand_DMs, cand_SNRs, s = 1, color = 'none', edgecolor='black')
        ax3.set(ylabel = 'Signal-to-noise ratio', xlabel = 'DM (cm$^{-3}$ pc)')
        ax3.yaxis.set_minor_locator(AutoMinorLocator())
        ax3.xaxis.set_minor_locator(AutoMinorLocator())
        ax3.tick_params(axis = "both", direction = "in", which = 'both',  top = True, right = True)
        ax3.margins(x=0) 


        snr_range = 12.0
        cand_symbols = (cand_SNRs-threshold)/snr_range * 6.0 + 20.5
        cand_symbols = cand_symbols.astype(np.int32)
        cand_symbols[cand_symbols>26] = 500

        ax4.scatter(cand_ts, cand_DMs, cand_SNRs, color='none', edgecolor='black')
        ax4.set(xlabel = 'Time (s)', ylabel = 'DM (cm$^{-3}$ pc)')
        ax4.xaxis.set_minor_locator(AutoMinorLocator())
        ax4.yaxis.set_minor_locator(AutoMinorLocator())
        ax4.tick_params(axis = "both", direction = "in", which = 'both',  top = True, right = True)
        ax4.margins(x=0) 

        plt.show()
