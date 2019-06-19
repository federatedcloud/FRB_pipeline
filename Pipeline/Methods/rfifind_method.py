from method import *

import sys
import os
import time
from glob import glob


def main(d):

    print("Running PRESTO rfifind")
    t_rfi_start = time.time()
    
    # get/set file locations
    directory= d['directory']
    rfi_dir = d['rfi_dir']
    basename = d['basename']
    fitslist = glob('%s/%s*.fits' %(directory, basename))
    fitslist.sort()
    fitsfiles = ' '.join(fitslist)
    
    # get parameters from dictionary
    rfi_flags = d['rfi_flags']
    rfi_otherflags = d['rfi_otherflags'] + ' '
    
    # run command    
    cmd = 'rfifind -o %s %s %s %s' %(basename, rfi_flags, rfi_otherflags, fitsfiles)
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
