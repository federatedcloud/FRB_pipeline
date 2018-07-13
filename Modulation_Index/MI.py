# Python 2.7
import sys
import math
import numpy as np
from astropy.io import fits

import os
import os.path

def dedisp_smooth(data, delays, nchan, downfact, spec, mean):
    temp=0.0
    for i in range(nchan):
        temp=0.0
        for j in range(int(downfact)):
#            n = nchan*delays[i] + i + nchan*j
#            print n
            n=1
            temp = temp + (data[n] - mean)
        spec[i]= temp/downfact

def calc_chandelays(delays, dm, freq_lo, bw, nchan, tsamp):
    #freq_hi,tedelay, floc, dnu, bw_corr=0.0
    
    dnu = bw/nchan               #Channel resolution
    freq_hi = freq_lo + bw-dnu   #Center freq of highest bin
    bw_corr = bw - dnu           #Bandwidth from center of top and bottom bins

    for i in range(nchan):
        floc = freq_lo + dnu*i
        tdelay = 4.15e6*dm*(1.0/(floc*floc) - 1.0/(freq_hi*freq_hi))  #Modulation Index
        delays[i] = round(tdelay/tsamp) 


#Global for now
#nchan=960;
nchan=3
left_chan=0
right_chan=2
#left_chan=12;
#right_chan=948;
bw=322.617;  #Bandwidth of entire band
freq_lo=1214.2896
tsamp=0.065476

#DM      Sigma      Time (s)     Sample    Downfact
a=(77.00,  5.14,     11.228643,      42873,       3)
b=(77.00,  5.09,     20.800214,      79419,      30)
c=(78.00,  5.43,     41.005643,     156567,      30)
data=np.array([a,b,c],dtype=np.float)
print 'data',data
#print data[:,2]
#data=[0]*(MAX_BYTES + 1)

       
delays=[0]*(nchan + 1) #int
spectrum=[0.0]*(nchan + 1) #float 

dm_0 = -1.0
#Define the number of channels excluding edges
loc_nchan=right_chan-left_chan

i=0
for i in range(len(data)):
    dm = data[i,0]
    snr = data[i,1]
    stime = data[i,2]
    snum = data[i,3]
    downfact = data[i,4]
#RESET VARIABLES
    Ibar =0.0
    Ibar2=0.0
    dmean = 5.0 #!dmean/=nchan #???
    if(dm != dm_0):
    #Get delays
        calc_chandelays(delays=delays, dm=dm, freq_lo=freq_lo, bw=bw, nchan=nchan, tsamp=tsamp) #return delays[
    
        max_dm_delay=delays[0]   #???

#SMOOTH and DEDISPERE DATA
    dedisp_smooth(data, delays, nchan, downfact, spectrum, dmean)

#CALC Ibar and I2bar
    for ii in range(left_chan, right_chan):
        Ibar = Ibar + spectrum[ii]
        Ibar2 = Ibar2 + spectrum[ii]**2
        #Ibar = Ibar + (spectru[ii]-dmean)
        #Ibar2 = Ibar2 + (spectru[ii]-dmean)**2
    Ibar/=loc_nchan
    Ibar2/=loc_nchan
    m_I=np.sqrt(Ibar2-Ibar*Ibar)/Ibar
    print 'mi',m_I
#SAVE Results  ???
#    data_mi[i] = [dm, snr, stime, snum, downfact, Ibar, Ibar2, m_I]
            
    dm_0 = dm


print dm,snr,stime,snum,downfact,Ibar,Ibar2,m_I
