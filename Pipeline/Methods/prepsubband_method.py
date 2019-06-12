from method import *

import time
from readhdr import get_samples
import psr_utils
from glob import glob

def main(d):

    print("Running PRETO prepsubband.")
    t_prep_start = time.time()

    # get/set file locations
    fits_dir = d['directory']
    rfi_dir= fits_dir
    prep_dir = fits_dir
    basename = d['basename']
    fitslist = glob('%s/%s*.fits' %(fits_dir, basename))
    fitslist.sort()
    fitsfiles = ' '.join(fitslist)
    
    # get de-dispersion parameters
    prep_usemask = bool(d['prep_usemask'])
    dmlow = float(d['dmlow'])
    ddm = float(d['ddm'])
    ndm = int(d['ndm'])
    downsample = float(d['downsample'])
    nsub = int(d['nsub'])
    prep_otherflags = d['prep_otherflags'] #str

    # run prepsubband command
    print("Dedispersing with 1st batch of DMs")
    orig_N = get_samples(fitslist, d['filetype'])
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
    try_cmd(cmd)

    # move output to prep_dir
    mv_cmd1 = 'mv %s %s' %(work_dir+'/*.dat', prep_dir)
    mv_cmd2 = 'mv %s %s' %(work_dir+'/*.inf', prep_dir)
    try_cmd(mv_cmd1)
    try_cmd(mv_cmd2)

    t_prep_end = time.time()
    prep_time = (t_prep_end - t_prep_start)
    print("PRESTO prepsubband took %f seconds." %(prep_time))

    return d
