from method import *
import numpy as np
import os

#   include <stdio.h>
#   include <stdlib.h>
#   include <math.h>
#   include "mock_spec.h"

#   define BYTES_SAMP 1
#   define MAX_BYTES 35000000

def main(combined_file, filename_mask, filename_output):

    # kDM is a constant
    # right_chan, left_chan, nchan
    # freq_lo, bw, dt

    # Open Files
    if not os.path.exists(combined_file):
        print("Path to combined single_pulse file does not exist or is incorrect. Quitting.")
    else:
        fin= open(combined_file, 'r')
    if not os.path.exists(filename_mask):
        print("Path to masked_data_file does not exist or is incorrect. Quitting.")
    else:
        masked_data_npz= np.load(filename_mask)
        print("Found masked_data_file.")
    if not os.path.exists(filename_output):
        print("Path to output_file does not exists. Creating new output_file."
        fout= open(filename_output, 'w+')
    else:
        fout= open(filename_output, 'w')

    # Define the number of channels including edges
    loc_nchan= right_chan - left_chan

    line= fin.readline()
    dm_prev= -1.0
    while (len(line) > 0):
        
        # Read Info from SinglePulse file
        clist= line.split()  # current list
        dm= float(clist[0])
        snr= float(clist[1])
        stime= float(clist[2])
        snum= int(clist[3])
        downfact= float(clist[4])
        block= int(clist[5])
        rms= float(clist[6])
        dmean= float(clist[7])

        # Reset Variables
        Ibar= 0.0
        Ibar2= 0.0
        dmean /= nchan
    
        # Calculate channel delays
        if (dm!= dm_prev):
            delays= calc_chandelays(dm, kDM, freq_lo, bw, nchan, dt)
            max_dm_delay= delays[0]
            # "Tare" the spectrum
            for j in range(nchan):
                spectrum[j]= 0.0
        
        # Load the appropriate Data array
        tstart_bin= int(stime/dt)
        tend_bin= tstart_bin + downfact + max_dm_delay
        data= masked_data_npz[masked_data_npz.files[0]][:, tstart_bin:tend_bin]
        
        # Calculate Spectrum
        spectrum= dedisp_smooth(data, delays, nchan, downfact, dmean)
        for j in range(right_chan - left_chan):
            val= spectrum[j + left_chan]
            Ibar+= val
            Ibar2+= val**2
        Ibar/= loc_nchan
        Ibar2/= loc_nchan
    
        m_I= sqrt(Ibar2 - Ibar**2) / Ibar
        output_file.write("%f   %f   %lf   %u   %f   %lf   %lf   %lf\n", %(dm, snr, stime, snum, downfact, Ibar, Ibar2, m_I))
        dm_prev= dm        
        line= fin.readline()

    # close files
    fin.close()
    fout.close()  


def dedisp_smooth(data, delays, nchan, t_wid, mean):

    spec= np.zeros(nchan)
    for vbin in range(nchan):
        tmp= 0.0
        for i in range(t_wid):
            tbin= delays[vbin] + i
            tmp+= data[vbin, tbin] - mean
        spec[vbin]= tmp / t_wid
    
    return spec

def calc_chandelays(dm, kDM, freq_lo, bw, nchan, dt):

    dnu= bw / nchan     # channel resolution
    bw_corr= bw - dnu   # bandwidth from center of top and bottom bins
    freq_hi= freq_lo + bw_corr  # center freq of highest bin
    delays= np.zeros(nchan)
    
    for j in range(nchan):
        floc= freq_lo + (dnu * j)
        tdelay= kDM * dm * (1.0/(floc**2) - 1.0/(freq_hi**2))
        delays[j]= int((tdelay / dt) + 0.5)

    return delays
