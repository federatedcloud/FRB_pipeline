# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 09:14:18 2018

@author: shen
"""

# Python 2.7
import sys
import math
import numpy as np

import pyfits

from astropy.io import fits



import os
import os.path

#Global for now
nchan=960;
left_chan=12;
right_chan=948;
bw=322.617;  #Bandwidth of entire band
freq_lo=1214.2896
tsamp=0.065476

BYTES_SAMP = 1  #Show twice
MAX_BYTES = 35000000  #Show once

data_mi=[]

#Func dedisp_smooth(unsigned char *data, unsigned int *delays, int nchan, float t_wid, double *spec, double mean)
def dedisp_smooth(data, delays, nchan, downfact, spec, mean):
    temp=0.0
    for i in range(nchan):
        temp=0.0
        for j in range(downfact):
            n = nchan*delays[i] + i + nchan*j
            temp = temp + (data[n] - mean)
        spec[i]= temp/downfact


#Func calc_chandelays(unsigned char *data, unsigned int *delays, int nchan, float t_wid, double *spec, double mean);
#freq_lo = center frequency of the lowest channel;bw = bandwidth from edge to edge;tsamp = sample time in msec
def calc_chandelays(delays, dm, freq_lo, bw, nchan, tsamp):
    #freq_hi,tedelay, floc, dnu, bw_corr=0.0
    
    dnu = bw/nchan               #Channel resolution
    freq_hi = freq_lo + bw-dnu   #Center freq of highest bin
    bw_corr = bw - dnu           #Bandwidth from center of top and bottom bins  ???no use???
    for i in range(nchan):
        floc = freq_lo + dnu*i
        tdelay = 4.15e6*dm*(1.0/(floc*floc) - 1.0/(freq_hi*freq_hi))  #Modulation Index
        delays[i] = int(round(tdelay/tsamp))  # Python 2.7

#Main fun(sp_data .sp, raw_ _mask.fits, test_MF.mi)
def calc_mi(sp_data,raw_data,output_file_name):
    '''
    raw_data = raw_data_with_mask.fits
    '''
    delays = [0]*(nchan + 1) #int
    spectrum = [0.0]*(nchan + 1) #float
    #data=[]*(MAX_BYTES + 1)
    
    dm_0 = -1.0
    loc_nchan=right_chan-left_chan;

    
    i=0
    for i in range(len(sp_data)):
        dm = sp_data[i,0]
        snr = sp_data[i,1]
        stime = sp_data[i,2]
        snum = sp_data[i,3]
        downfact = sp_data[i,4]
#RESET VARIABLES
        Ibar =0.0
        Ibar2=0.0
        dmean = 0.0
#        dmean /= nchan 
        if(dm != dm_0):
        #Get delays
            calc_chandelays(delays=delays, dm=dm, freq_lo=freq_lo, bw=bw, nchan=nchan, tsamp=tsamp) #return delays[]
            max_dm_delay=delays[0]   #//OK?no use?
            
        start_byte=nchan*(snum - (int(downfact)/2)*BYTES_SAMP)  #//Consider edges

        
        hdulist = pyfits.open('./raw_data_with_mask.fits') #raw_data
        data_in = hdulist[0].data
        
        #OR
#        vals = n * nsblk * nchan  #n=8, nsblk=15270, nchan=960
#        dat = np.fromfile(raw_data, dtype='float32', count=vals)
#        dat = np.reshape(dat, (-1, nchan))        
        
#//MOVE TO START BYTE
        data_raw = data_in.seek(start_byte,0)
        
#     //READ IN DATA
#        nbytes2read=BYTES_SAMP*nchan*(max_dm_delay + int(downfact));
#        nread=fread(data, sizeof(char), nbytes2read, fraw);
#


#SMOOTH and DEDISPERE DATA
        dedisp_smooth(data_raw, delays, nchan, downfact, spectrum, dmean)

#CALC Ibar and I2bar
        for ii in range(left_chan, right_chan):
            Ibar = Ibar + spectrum[ii]
            Ibar2 = Ibar2 + spectrum[ii]**2
            #Ibar = Ibar + (spectru[ii]-dmean)
            #Ibar2 = Ibar2 + (spectru[ii]-dmean)**2
        Ibar/=loc_nchan
        Ibar2/=loc_nchan
        m_I=np.sqrt(Ibar2-Ibar*Ibar)/Ibar


#SAVE Results       
#        data_mi[i] = [dm, snr, stime, snum, downfact, Ibar, Ibar2, m_I]
        data_mi.append([dm, snr, stime, snum, downfact, Ibar, Ibar2, m_I])
        dm_0 = dm
        
    fits.writeto("./data_mi.fits", data_mi)
