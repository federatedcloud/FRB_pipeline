from method import *

import sys
import os
import time
from glob import glob


def main(d):

    print("Running PRESTO rfifind")
    t_rfi_start = time.time()
    
    # get/set file locations 
    fits_dir = d['directory']
    rfi_dir = d['work_dir'] + d['rfi_dir_name']
    fitsname = d['basename']
    fitslist = glob('%s/%s*.fits' %(fits_dir, fitsname))
    fitslist.sort()
    fitsfiles = ' '.join(fitslist)
    
    # get parameters from dictionary
    rfi_time = int(float(d['rfi_time']))
    tsig = float(d['tsig'])
    fsig = float(d['fsig'])
    chanfrac = float(d['chanfrac'])
    intfrac = float(d['intfrac'])
    rfi_otherflags = d['rfi_otherflags'] + ' '
    
    # run command    
    cmd = 'rfifind -psrfits -o %s -time %d -timesig %f -freqsig %f '\
          '-chanfrac %f -intfrac %f %s %s' %(fitsname, rfi_time, tsig, fsig,
                                             chanfrac, intfrac, rfi_otherflags,
                                             fitsfiles)
    try_cmd(cmd)
   
    # move products to rfi_products directory 
    if not os.path.exists(rfi_dir):
        os.makedirs(rfi_dir)

    cmd = 'mv ./*rfifind.* ' + rfi_dir
    try_cmd(cmd)
    
    t_rfi_end = time.time()
    rfi_time = (t_rfi_end - t_rfi_start)
    print("RFI Flagging took %f seconds" %(rfi_time))
    
    return d
