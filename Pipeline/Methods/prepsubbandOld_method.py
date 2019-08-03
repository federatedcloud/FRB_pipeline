from method import *

import time
from readhdr import get_samples
import psr_utils
from glob import glob

def main(hotpotato):

    print("Running PRETO prepsubband.")
    t_prep_start = time.time()

    # get/set file locations
    fits_dir = get_value(hotpotato, 'directory')
    rfi_dir= fits_dir
    prep_dir = fits_dir
    basename = get_value(hotpotato, 'basename')
    fitslist = glob('%s/%s*.fits' %(fits_dir, basename))
    fitslist.sort()
    fitsfiles = ' '.join(fitslist)
    
    # get de-dispersion parameters
    prep_usemask = bool(get_value(hotpotato, 'prep_usemask'))
    dmlow = float(get_value(hotpotato, 'dmlow'))
    ddm = float(get_value(hotpotato, 'ddm'))
    ndm = int(get_value(hotpotato, 'dmspercall'))
    downsample = float(get_value(hotpotato, 'downsample'))
    nsub = int(get_value(hotpotato, 'nsub'))
    prep_otherflags = get_value(hotpotato, 'prep_otherflags') #str

    # run prepsubband command
    print("Dedispersing with 1st batch of DMs")
    orig_N = get_samples(fitslist, get_value(hotpotato, 'filetype'))
    numout = psr_utils.choose_N(orig_N)
    print(orig_N, numout)

    if prep_usemask == True:
        # make sure rfi_find has been run previously
        try:
            rfi_maskname = glob(rfi_dir+'/*.mask')[0]
        except IndexError:
            raise Exception("Could not access RFI_mask fits file. Please run PRESTO rfifind "\
                           "before generating masked dynamic spectrum.")

        cmd = 'prepsubband -o %s -psrfits -nsub %d -numout %d -lodm %.6f -dmstep %.6f '\
            '-numdms %d -downsamp %d %s -mask %s %s' %(basename, nsub, numout/downsample,
                                                                dmlow, ddm, ndm, downsample,
                                                                prep_otherflags, rfi_maskname, 
                                                                fitsfiles)
    else:
        cmd = 'prepsubband -o %s -psrfits -nsub %d -numout %d -lodm %.6f -dmstep %.6f '\
            '-numdms %d -downsamp %d  %s %s' %(basename, nsub, numout/downsample,
                                                        dmlow, ddm, ndm, downsample,
                                                        prep_otherflags, fitsfiles)

        cmd = 'prepsubband -o %s % %s' %(basename, prep_flags, prep_otherflags) 

    try_cmd(cmd)

    # move output to prep_dir
    mv_cmd1 = 'mv %s %s' %(work_dir+'/*.dat', prep_dir)
    mv_cmd2 = 'mv %s %s' %(work_dir+'/*.inf', prep_dir)
    try_cmd(mv_cmd1)
    try_cmd(mv_cmd2)

    t_prep_end = time.time()
    prep_time = (t_prep_end - t_prep_start)
    print("PRESTO prepsubband took %f seconds." %(prep_time))

    return hotpotato
