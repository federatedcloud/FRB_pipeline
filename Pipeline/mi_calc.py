from method import *
import numpy as np
import os

#   include <stdio.h>
#   include <stdlib.h>
#   include <math.h>
#   include "mock_spec.h"

#   define BYTES_SAMP 1
#   define MAX_BYTES 35000000

def main(combined_file, masked_data_file, output_file):

    ### fin, fraw, fout
    # dm, snr, downfact
    # stime, rms, dmean
    # ii, snum, block, loc_nchan
    # dm_prev= -1.0
    # start_byte, num_bytes, max_dm_delay
    # nread, nbytes2read, nscanned
    # Ibar, Ibar2, m_I

    # Open Files
    if not os.path.exists(combined_file):
        print("Path to combined single_pulse file does not exist or is incorrect. Quitting.")
    else:
        fin= open(combined_file, 'r')
    if not os.path.exists(masked_data_file, 'r'):
        print("Path to masked_data_file does not exist or is incorrect. Quitting.")
    else:
        fraw= open(masked_data_file, 'r')
    if not os.path.exists(output_file):
        print("Path to output_file does not exists. Creating new output_file."
        fout= open(output_file, 'w+')
    else:
        fout= open(output_file, 'w')

    data= np.zeros(??????)
    delays= np.zeros(nchan)
    spectrum= np.zeros(nchan)
    
    # Define the number of channels including edges
    loc_nchan= right_chan - left_chan

    line= fin.readline()
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
            delays= calc_chandelays(dm, freq_lo, bw, nchan, tsamp)
            for j in range(nchan):
                spectrum[j]= 0.0
                max_dm_delay= delays[0]
        
        # Calculate byte shit
        start_byte= nchan * (snum - int(downfact/2.)) * BYTES_SAMP
        fraw.seek(start_byte, 0)
        nbytes2read= nchan * (max_dm_delay + int(downfact))
        data= fraw.read(sys.getsizeof('.') * nbytes2read)
#        nread=fread(data, sizeof(char), nbytes2read, fraw)

        # Calculate Spectrum
        spectrum= dedisp_smooth(data, delays, nchan, downfact, dean)
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
    fraw.close()
    fout.close()  


def dedisp_smooth(data, delays, nchan, t_wid, mean):

    spec= np.zeros(nchan)
    for j in range(nchan):
        tmp= 0.0
        for i in range(t_wid):
            n= (nchan * delays[j]) + j + (nchan * i)
            tmp+= data[n] - mean
        spec[j]= tmp / t_wid
    
    return spec

def calc_chandelays(dm, freq_lo, bw, nchan, tsamp):

    dnu= bw / nchan     # channel resolution
    bw_corr= bw - dnu   # bandwidth from center of top and bottom bins
    freq_hi= freq_lo + bw_corr  # center freq of highest bin
    delays= np.zeros(nchan)
    
    for j in range(nchan):
        floc= freq_lo + (dnu * j)
        tdelay= 4.15e6 * dm * (1.0/(floc**2) - 1.0/(freq_hi**2))
        delays[j]= (tdelay / tsamp) + 0.5

    return delays
