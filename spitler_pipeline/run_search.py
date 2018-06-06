import os
import sys
import time
import sifting
import re
import shlex
import psr_utils
import readhdr
import subprocess as sp
import multiprocessing as mp
from glob import glob

import params
import make_plots

class Timer:
    def __init__(self):
        self.combine_mocks = 0.0
        self.rfifind = 0.0
        self.prepsubband = 0.0
        self.realfft = 0.0
        self.accelsearch = 0.0
        self.presto_sp = 0.0
        self.mod_index = 0.0
        self.total = 0.0

    def print_summary(self):
        print "\n****************************************************"
        print "                  TIME SUMMARY                      "
        print "****************************************************"
        print "\n"
        print "Program:                         Running Time (min): "
        print "--------                         -----------------  "
        print "combine_mocks                        %.2f" %(self.combine_mocks/60.)
        print "rfifind                              %.2f" %(self.rfifind/60.)
        print "prepsubband                          %.2f" %(self.prepsubband/60.)
        print "realfft                              %.2f" %(self.realfft/60.)
        print "accelsearch                          %.2f" %(self.accelsearch/60.)
        print "single_pulse_search                  %.2f" %(self.presto_sp/60.)
        print "palfa_calc_mi                        %.2f" %(self.mod_index/60.)
        print "\n"
        print "Total Runtime = %.2f min" %(self.total/60.)

    def write_summary(self, outfile):
        fout = open(outfile, 'w')
        fout.write( "\n****************************************************\n")
        fout.write( "                  TIME SUMMARY                      \n")
        fout.write( "****************************************************\n")
        fout.write( "\n"                                                     )
        fout.write( "Program:                         Running Time (min): \n")
        fout.write( "--------                         -----------------  \n")
        fout.write( "combine_mocks                        %.2f\n" %(self.combine_mocks/60.))
        fout.write( "rfifind                              %.2f\n" %(self.rfifind/60.))
        fout.write( "prepsubband                          %.2f\n" %(self.prepsubband/60.))
        fout.write( "realfft                              %.2f\n" %(self.realfft/60.))
        fout.write( "accelsearch                          %.2f\n" %(self.accelsearch/60.))
        fout.write( "single_pulse_search                  %.2f\n" %(self.presto_sp/60.))
        fout.write( "palfa_calc_mi                        %.2f\n" %(self.mod_index/60.))
        fout.write( "\n"                                                   )
        fout.write( "Total Runtime = %.2f min\n" %(self.total/60.))
        fout.close()


def check_dependencies(work_dir, fits_dir, fitsbase):
    """
    Since we allow for some processing steps to be skipped, we need
    to check to make sure that all depedencies are still in place.
    This function checks for these dependencies and exits with a 
    descriptive error if they do not exist
    """
    # Print to screen what processing steps have been selected
    print "The following processing steps have been selected:\n"
    if params.do_combine_mocks:
        print "   - PALFA2 psrfits_utils combine_mocks"
    if params.do_rfifind:
        print "   - PRESTO rfifind (RFI mitigation tools)"
    if params.do_prepsub:
        print "   - PRESTO prepsubband (dedispersion)"
    if params.do_candsearch:
        print "   - PRESTO acceleration search and candidate sifting"
    if params.do_presto_sp:
        print "   - PRESTO singlepulse search (singlepulse.py)"
    if params.do_mod_index:
        print "   - PALFA2 modulation index calculation"
    if params.do_make_plots:
        print "   - Plot single pulse candidates that meet mi threshold"
    # Print to screen what processing steps are being skipped
    print "\nThe following processing steps are being skipped:\n"
    if params.do_combine_mocks == 0:
        print "   - PALFA2 psrfits_utils combine_mocks"
    if params.do_rfifind == 0:
        print "   - PRESTO rfifind (RFI mitigation tools)"
    if params.do_prepsub == 0:
        print "   - PRESTO prepsubband (dedispersion)"
    if params.do_candsearch == 0:
        print "   - PRESTO acceleration search and candidate sifting"
    if params.do_presto_sp == 0:
        print "   - PRESTO singlepulse search (singlepulse.py)"
    if params.do_mod_index == 0:
        print "   - PALFA2 modulation index calculation"
    if params.do_make_plots == 0:
        print "   - Plot single pulse candidates that meet mi threshold"
    print "\nChecking dependencies...\n"
    # There must be at least one .fits file in the fits directory
    fl = glob(fits_dir + '/%s*.fits' %fitsbase)
    if len(fl):
        print "  Found %d file(s) in %s:\n" %(len(fl), fits_dir)
        for i in fl:
            print "    %s\n" %(i.split('/')[-1])
    else:
        print "  No %s*.fits files found in %s !\n    Exiting...\n" %(fitsbase, fits_dir)
        sys.exit(0)
    # If skipping the RFIFIND step in processing but want to do
    # processing steps further down the line, then there must be a
    # rfi_products folder in the results directory with a .mask file
    # in it
    if params.do_rfifind == 0 and params.use_mask and \
            (params.do_prepsub or params.do_candsearch or params.do_presto_sp):
        mlist = glob(work_dir + '/rfi_products/*.mask')
        if len(mlist):
            print "  Using RFI .mask:\n    %s\n" %(mlist[0])
        else:
            print "  No RFI .mask found in %s/rfi_products!\n    Exiting...\n"\
                %(work_dir)
            sys.exit(0)
    # If skipping the PREPSUBBAND step in processing but want to
    # do processing steps further down the line, then there must be
    # de-dispersed time series files in the results directory of
    # the form basename*DM*.dat and basename*DM*.inf
    if params.do_prepsub == 0 and (params.do_candsearch or 
                                  params.do_presto_sp):
        dats = glob(work_dir + '/*DM*dat')
        infs = glob(work_dir + '/*DM*inf')
        if not (len(dats) and len(infs)):
            print "  No .dat and/or .inf files in %s!\n    Exiting...\n" %(work_dir)
            sys.exit(0)
    # If we haven't exited by now, then things should be good
    print "\nLooks good...\n\n"
    # Pause for a few seconds so you can actually read the output
    time.sleep(5)

def format_name(name_dir):
    """
    Remove trailing '/' on path names (for consistency)
    """
    if(name_dir.endswith('/')):
        name_dir = name_dir.rstrip('/')
    return(name_dir)

def try_cmd(cmd, stdout=None, stderr=None):
    """
    Run the command in the string cmd using sp.check_call().  If there
    is a problem running, a CalledProcessError will occur and the
    program will quit.
    """
    print "\n\n %s \n\n" %cmd
    try:
        retval = sp.check_call(cmd, shell=True, stdout=stdout, stderr=stderr, executable='/bin/bash')
    except sp.CalledProcessError:
        print("The command:\n %s \ndid not work, quitting..." %cmd)
        sys.exit(0)

def run_combine_mocks(file1, file2, basename, fits_dir):
    print("Combining 2 fits files")
    t_combine_start = time.time()
    
    file1full = "%s/%s.fits" %(fits_dir, file1)
    file2full = "%s/%s.fits" %(fits_dir, file2) 
    fitsname = "%s/%s" %(fits_dir, basename)
    
    cmd = "combine_mocks %s %s -o %s" % (file1full, file2full, fitsname)
    try_cmd(cmd)
    
    t_combine_end = time.time()
    dt = t_combine_end - t_combine_start
    print("\nCombining files took %f minutes\n" %(dt/60.))
    return dt

def run_rfifind(fitslist, fitsname, work_dir):
    print("Running rfifind on the psrfits files")
    t_rfi_start = time.time()

    fitsfiles = ' '.join(fitslist) 

    # Get flag values from params file
    rfi_time = params.rfi_time
    tsig     = params.time_sig
    fsig     = params.freq_sig
    chanfrac = params.chan_frac
    intfrac  = params.int_frac
    other_flags = params.rfi_otherflags

    cmd = 'rfifind -psrfits -o %s -time %d -timesig %f -freqsig %f '\
          '-chanfrac %f -intfrac %f %s %s' %(fitsname, rfi_time, tsig, fsig,
                                             chanfrac, intfrac, other_flags,
                                             fitsfiles)
    try_cmd(cmd)
    # If no directory exists for the rfi products, make one
    # and move them over
    rfi_dir = work_dir+'/rfi_products'
    if not os.path.exists(rfi_dir):
        os.makedirs(rfi_dir)

    cmd = 'mv ./*rfifind* '+rfi_dir
    try_cmd(cmd)

    t_rfi_end = time.time()
    rfi_time = (t_rfi_end-t_rfi_start)
    print("RFI Flagging took %f hours" %(rfi_time/3600.))
    return rfi_time

def run_prepsubband(basename, maskname, fitslist, dmlow=params.dmlow, \
                        ddm=params.ddm, ndm=params.dmspercall, \
                        downsample=params.downsample, nsub=params.nsub):
    t_prep_start = time.time()
    fitsfiles = ' '.join(fitslist) 
    print("Dedispersing with 1st batch of DMs")
    orig_N = readhdr.get_samples(fitslist, params.dat_type)
    numout = psr_utils.choose_N(orig_N)
    print(orig_N, numout)

    other_flags = params.prep_otherflags
    if params.use_mask:
        cmd = 'prepsubband -o %s -psrfits -nsub %d -numout %d -lodm %.6f -dmstep %.6f '\
            '-numdms %d -downsamp %d %s -mask %s %s' %(basename, nsub, numout/downsample, 
                                                                 dmlow, ddm, ndm, downsample,
                                                                 other_flags, maskname, fitsfiles)
    else:
        cmd = 'prepsubband -o %s -psrfits -nsub %d -numout %d -lodm %.6f -dmstep %.6f '\
            '-numdms %d -downsamp %d  %s %s' %(basename, nsub, numout/downsample,
                                                        dmlow, ddm, ndm, downsample,
                                                        other_flags, fitsfiles)

    try_cmd(cmd)

    t_prep_end = time.time()
    dt = t_prep_end - t_prep_start
    print "De-dispersion took %.2f hours.\n" %(dt/3600.)
    return dt

def multi_call_prepsubband(basename, maskname, fitslist, dmlow=params.dmlow, \
                               ddm=params.ddm, downsample=params.downsample, \
                               dmcalls=params.dmcalls, nsub=params.nsub,  \
                               dsubDM=params.dsubDM, \
                               dmspercall=params.dmspercall):
    t_prep_start = time.time()
    fitsfiles = ' '.join(fitslist)

    orig_N = readhdr.get_samples(fitslist, params.dat_type)
    numout = psr_utils.choose_N(orig_N)
    other_flags = params.prep_otherflags

    # Downsample organization as in PRESTO dedisp.py (why?)
    sub_downsample = downsample / 2
    dat_downsample = 2
    if downsample < 2: sub_downsample = dat_downsample = 1

    print("Dedispersing using %d calls on %d subbands\n" %(dmcalls, nsub))
    for ii in xrange(dmcalls):
        subDM = dmlow + (ii+0.5)*dsubDM
        # Make subband
        if params.use_mask:
            cmd_sub = "prepsubband -o %s -sub -subdm %.2f -nsub %d -downsamp %d %s -mask %s %s" \
                %(basename, subDM, nsub, sub_downsample, other_flags, maskname, fitsfiles)
        else:
            cmd_sub = "prepsubband -o %s -sub -subdm %.2f -nsub %d -downsamp %d %s %s" \
                %(basename, subDM, nsub, sub_downsample, other_flags, fitsfiles)
        try_cmd(cmd_sub)
        
        # Get dedispersed time series
        sub_dmlow = dmlow + ii*dsubDM
        subfiles =  basename+"_DM%.2f.sub[0-9]*" %subDM
        if params.use_mask:
            cmd_dat = "prepsubband -o %s -numout %d -lodm %.2f -dmstep %.2d "\
                "-numdms %d -downsamp %d %s -mask %s %s" \
                %(basename, numout/downsample, sub_dmlow, ddm, dmspercall, dat_downsample, other_flags, maskname, subfiles)
        else:
            cmd_dat = "prepsubband -o %s -numout %d -lodm %.2f -dmstep %.2d "\
                "-numdms %d -downsamp %d %s %s" \
                %(basename, numout/downsample, sub_dmlow, ddm, dmspercall, dat_downsample, other_flags, subfiles)
        try_cmd(cmd_dat)
    
    t_prep_end = time.time()
    dt = t_prep_end - t_prep_start
    print "De-dispersion took %.2f hours.\n" %(dt/3600.)
    return dt


def accelsift_old(filenm):
    """
    This function is a translation of the PRESTO code ACCEL_sift.py
    so that it can be more easily incorporated into our code.  It 
    sifts through the ACCEL cands, making cuts on various parameters
    and removing duplicates and harmonics.
    """
    # Set a bunch of parameters from our params.py file
    min_num_DMs             = params.min_num_DMs
    low_DM_cutoff           = params.low_DM_cutoff
    sifting.sigma_threshold = params.sigma_threshold
    sifting.c_pow_threshold = params.c_pow_threshold
    sifting.known_birds_p   = params.known_birds_p
    sifting.known_birds_f   = params.known_birds_f
    sifting.r_err           = params.r_err
    sifting.short_period    = params.short_period
    sifting.long_period     = params.long_period
    sifting.harm_pow_cutoff = params.harm_pow_cutoff
    
    # Try to read the .inf files first, as _if_ they are present, all of    
    # them should be there.  (if no candidates are found by accelsearch     
    # we get no ACCEL files... 
    inffiles = glob("*.inf")
    candfiles = glob("*ACCEL_" + str(params.zmax))
    # Check to see if this is from a short search                                         
    if len(re.findall("_[0-9][0-9][0-9]M_" , inffiles[0])):
        dmstrs = [x.split("DM")[-1].split("_")[0] for x in candfiles]
    else:
        dmstrs = [x.split("DM")[-1].split(".inf")[0] for x in inffiles]
    dms = map(float, dmstrs)
    dms.sort()
    dmstrs = ["%.2f"%x for x in dms]

    # Read in all the candidates
    cands = sifting.read_candidates(candfiles)
    # Remove candidates that are duplicated in other ACCEL files
    if len(cands):
        cands = sifting.remove_duplicate_candidates(cands)
    # Remove candidates with DM problems
    if len(cands):
        cands = sifting.remove_DM_problems(cands, min_num_DMs, dmstrs, low_DM_cutoff)
    # Remove candidates that are harmonically related to each other
    # Note:  this includes only a small set of harmonics
    if len(cands):
        cands = sifting.remove_harmonics(cands)
    # Write candidates to STDOUT
    if len(cands):
        cands.sort(sifting.cmp_snr)
        sifting.write_candlist(cands, candfilenm=filenm)


def accelsift(filenm):
    """
    This function is a translation of the PRESTO code ACCEL_sift.py
    so that it can be more easily incorporated into our code.  It 
    sifts through the ACCEL cands, making cuts on various parameters
    and removing duplicates and harmonics.
    """
    # Set a bunch of parameters from our params.py file
    min_num_DMs             = params.min_num_DMs
    low_DM_cutoff           = params.low_DM_cutoff
    sifting.sigma_threshold = params.sigma_threshold
    sifting.c_pow_threshold = params.c_pow_threshold
    sifting.known_birds_p   = params.known_birds_p
    sifting.known_birds_f   = params.known_birds_f
    sifting.r_err           = params.r_err
    sifting.short_period    = params.short_period
    sifting.long_period     = params.long_period
    sifting.harm_pow_cutoff = params.harm_pow_cutoff
    
    # Try to read the .inf files first, as _if_ they are present, all of    
    # them should be there.  (if no candidates are found by accelsearch     
    # we get no ACCEL files... 
    inffiles = glob("*.inf")
    
    # Check to see if this is from a short search                                         
    if len(re.findall("_[0-9][0-9][0-9]M_" , inffiles[0])):
        dmstrs = [x.split("DM")[-1].split("_")[0] for x in candfiles]
    else:
        dmstrs = [x.split("DM")[-1].split(".inf")[0] for x in inffiles]
    dms = map(float, dmstrs)
    dms.sort()
    dmstrs = ["%.2f"%x for x in dms]
    
    lo_candfiles = glob("*ACCEL_0")
    hi_candfiles = glob("*ACCEL_" + str(params.zmax))

    # Read in the lo-z candidates
    lo_cands = sifting.read_candidates(lo_candfiles)
    # Remove candidates that are duplicated in other ACCEL files
    if len(lo_cands):
        lo_cands = sifting.remove_duplicate_candidates(lo_cands)
    # Remove candidates with DM problems
    if len(lo_cands):
        lo_cands = sifting.remove_DM_problems(lo_cands, min_num_DMs, dmstrs, low_DM_cutoff)
    
    # Read in the hi-z candidates
    hi_cands = sifting.read_candidates(hi_candfiles)
    # Remove candidates that are duplicated in other ACCEL files
    if len(hi_cands):
        hi_cands = sifting.remove_duplicate_candidates(hi_cands)
    # Remove candidates with DM problems
    if len(hi_cands):
        hi_cands = sifting.remove_DM_problems(hi_cands, min_num_DMs, dmstrs, low_DM_cutoff)

    all_cands = lo_cands + hi_cands
    # Remove candidates that are harmonically related to each other
    # Note:  this includes only a small set of harmonics
    if len(all_cands):
        all_cands = sifting.remove_harmonics(all_cands)
   
    # Write candidates to STDOUT
    if len(all_cands):
        all_cands.sort(sifting.cmp_snr)
        sifting.write_candlist(all_cands, candfilenm=filenm)


def run_prepfold(filenm, outfile, errfile):
    """
    This function will run prepfold on the candidate files produced
    by the presto accelsearch.  This essentially replaces the
    gotocand.py script from the older version of the pipeline
    """
    # Open candfile
    f = open(filenm, 'r')
    
    i = 0
    for line in f:
        # This just skips down to where the files are
        if line.startswith('#'):
            i = 1
            continue
        if i==1:
            namecand = line.split()[0]
            #namesplit = namecand.split("_"+str(params.zmax)+":")
            namesplit = namecand.rsplit("_", 1)
            if len(namesplit) != 2:
                continue
            else:
                bname = namesplit[0]
                cnum  = namesplit[1].split(":")[1]
                psname = bname + "_Cand_" + cnum + ".pfd.ps"
                if os.path.exists(psname):
                    print "File "+psname+" already made, skipping"
                else:
                    candfile = namecand.split(':')[0] + '.cand'
                    datfile  = namecand.split('_ACCEL_')[0] + '.dat'
                    outname  = namecand.split('_ACCEL_')[0]
                    if ( os.path.exists(candfile) and os.path.exists(datfile) ):
                        cmd = "prepfold -noxwin -accelcand %s -accelfile %s -o %s %s"\
                              %(cnum, candfile, outname, datfile)
                        try_cmd(cmd, stdout=outfile, stderr=errfile)
                    else:
                        print "Could not find %s" %candfile
                        print "and/or         %s" %datfile
    # Close file, we're done
    f.close()


def run_one_fft(datfile, fft_out, fft_err):
    cmd = "realfft %s" %datfile
    fout = file(fft_out, 'a+')
    ferr = file(fft_err, 'a+')
    try_cmd(cmd, stdout=fout, stderr=ferr)

def run_realfft(workdir, basename):
    """
    Take FFT of all the dedispersed .dat files
    """
    t_fft_start = time.time()
    # Grab the .dat files
    datfiles = glob('*.dat')
    datfiles.sort()
    
    print("Will take FFTs of %d *.dat files\n" %len(datfiles))

    # Take FFTs using multiple cores
    ncores = params.accel_cores
    pool_accel = mp.Pool(processes=ncores)
    fft_out = 'fft.out'
    fft_err = 'fft.err'
    for datfile in datfiles:
        current_nm = datfile.split('.dat')[0] + '.fft'
        if os.path.exists(current_nm):
            print "File " + current_nm + "already made, skipping"
        else:
            arg_tup = (datfile, fft_out, fft_err)
            pool_accel.apply_async(func=run_one_fft, args=arg_tup)
    pool_accel.close()
    pool_accel.join()

    t_fft_end = time.time()
    dt = t_fft_end - t_fft_start
    return dt

def run_one_accel(datfile, zmax, nharm, flo, fhi, sigma_min, zap_str, suffix):
    fname = datfile.split('/')[-1].rstrip(suffix)
    accel_out = file(fname+'_accel.out', 'w')
    accel_err = file(fname+'_accel.err', 'w')
    cmd = 'accelsearch -zmax %d -numharm %d -flo %.6f -fhi %.6f -sigma %.2f %s %s' \
          %(zmax, nharm, flo, fhi, sigma_min, zap_str, datfile)
    try_cmd(cmd, stdout=accel_out, stderr=accel_err)

def run_accelsearch(work_dir, basename):
    """
    This function will run PRESTO's accelsearch on all the *.dat files
    in the current directory. The candidates ``sifted'' to remove
    candidates with obvious problems, harmonics, and duplicates. The
    final sifted list is written to a *.sifted.cands file.
    This function will also run prepfold on all the ACCEL cands
    The maximum accel bin, zmax, can be set in the params.py file.
    """
    t_accel_start = time.time()

    # Set data file suffix (.dat or .fft)
    if params.use_fft:
        suffix = '.fft'
    else:
        suffix = '.dat'
    datfiles = glob('*%s' %suffix)
    datfiles.sort()
    
    # Create files for the output and errors from accelsearch
    accel_out = file('accelsearch.out', 'w')
    accel_err = file('accelsearch.err', 'w')

    # Read in needed parameters from params file
    zmax  = params.zmax
    nharm = params.numharm
    flo   = params.freq_lo
    fhi   = params.freq_hi
    zap_str = params.zap_str
    ncores = params.accel_cores
    sigma_min = params.sigma_threshold
    
    # Run lo_accel accelsearch on each .dat file if we have not already done so
    print "Running lo-accel (z=0) accelsearch on %d %s files...\n" %(len(datfiles), suffix)
    pool_accel = mp.Pool(processes=ncores)
    for datfile in datfiles:
        current_nm = datfile.split(suffix)[0]
        current_nm = current_nm + "_ACCEL_" + str(0) + ".cand"
        if os.path.exists(current_nm):
            print "File " + current_nm + "already made, skipping"
        else:
            arg_tup = (datfile, 0, nharm, flo, fhi, sigma_min, zap_str, suffix)
            pool_accel.apply_async(func=run_one_accel, args=arg_tup)
    pool_accel.close()
    pool_accel.join()
    
    # Run hi_accel accelsearch on each .dat file if we have not already done so
    print "Running hi-accel (z=%d) accelsearch on %d %s files...\n" %(zmax, len(datfiles), suffix)
    pool_accel = mp.Pool(processes=ncores)
    for datfile in datfiles:
        current_nm = datfile.split(suffix)[0]
        current_nm = current_nm + "_ACCEL_" + str(params.zmax) + ".cand"
        if os.path.exists(current_nm):
            print "File " + current_nm + "already made, skipping"
        else:
            arg_tup = (datfile, zmax, nharm, flo, fhi, sigma_min, zap_str, suffix)
            pool_accel.apply_async(func=run_one_accel, args=arg_tup)
    pool_accel.close()
    pool_accel.join()
    
    # Make candsfile (if it doesn't exist), run the accel sifting function
    # on the cands, which sifts and outputs to file
    candsfilenm = basename + '.ACCEL_' + str(zmax) + '.sifted.cands'
    print "Sifting through the candidates...\n"
    accelsift(candsfilenm)

    # Run prepfold on the ACCEL files
    print "Running prepfold on the ACCEL cands...\n"
    run_prepfold(candsfilenm, accel_out, accel_err)

    # Make an output directory for the PRESTO cands
    outcand_dir = work_dir + "/cands_presto/"
    if not os.path.exists(outcand_dir):
        os.makedirs(outcand_dir)
    
    # Move the candidates over
    print "Moving candidates over to %s" %outcand_dir
    cmd = "mv %s/*ACCEL* %s" %(work_dir, outcand_dir)
    try_cmd(cmd)
    
    t_accel_end = time.time()
    dt = t_accel_end - t_accel_start
    return dt

def move_to_DM_dirs(work_dir, dmlow=params.dmlow, ddm=params.ddm, ndm=params.dmspercall):
    """
    Move the ACCEL text files and plots to sub-directories
    organized by trial DM
    """
    # Make PRESTO cands dir if it doesn't already exist
    outcand_dir = work_dir + "/cands_presto/"
    if not os.path.exists(outcand_dir):
        os.makedirs(outcand_dir)

    # Loop over DMs, make sub-dir, mv files
    dm_vals = [dmlow + ii * ddm for ii in xrange(ndm)]
    for dm in dm_vals:
        dm_dir = outcand_dir + "DM%.2f/" %dm
        if not os.path.exists(dm_dir):
            os.makedirs(dm_dir)
        cmd = "mv %s/*DM%.2f_ACCEL* %s" %(outcand_dir, dm, dm_dir)
        if len(glob("%s/*DM%.2f_ACCEL*" %(outcand_dir, dm))):
            try_cmd(cmd)
    return

def run_singlepulse_search(work_dir):
    sp_exe = params.singlepulse
    w_max = params.max_width 
    dfac  = params.dtrend 
    flags = params.sp_otherflags
    
    print("Looking for single pulses...\n")
    t_sp_start = time.time()
    #cmd = sp_exe+' -m '+str(w_max)+' '+work_dir+'/*.dat'
    if params.sp_modified:
        cmd = "%s -m %.6f %s %s/*.dat" %(sp_exe, w_max, flags, work_dir)
    else:
        cmd = "%s -m %.6f -d %d %s %s/*.dat" %(sp_exe, w_max, dfac, flags, work_dir)
    try_cmd(cmd)

    sp_dir = work_dir+'/single_pulse/'
    if not os.path.exists(sp_dir):
        os.makedirs(sp_dir)
    cmd = 'mv '+work_dir+'/*singlepulse* '+work_dir+'/single_pulse/'
    try_cmd(cmd)
    t_sp_end = time.time()
    dt = t_sp_end - t_sp_start
    return dt

def run_maskdata(maskname, basename):
    """
    Creates a masked dynamic spectrum called raw_data_with_mask.fits,
    which is the file needed for modulation index
    """
    print("Creating masked dynamic spectrum...\n")
    
    t_md_start = time.time()
    
    md_exec = "maskdata "
    filenamestr = params.fits_dir + "/" + basename + ".fits" #"thisisjusttoseeifitworks"
    cmd = md_exec + params.md_flags + maskname + params.md_otherflags + filenamestr
    try_cmd(cmd)
    
    t_md_end = time.time()
    dt = t_md_end - t_md_start
    return dt

def combine_sp_files(work_dir, basename):
    """
    Combines all the .singlepulse files from the single_pulse_search into a single .sp file
    that the modulation index calculation is expecting.
    """
    print("Combining .singlepulse files...\n")
    t_awk_start = time.time()
    sp_dir = work_dir+'/single_pulse/'
    
    awk_cmd = """awk '$1!="#" {print}' %s_DM*.singlepulse > %s_MF.sp""" %(basename, basename)
    cmd = "(pushd %s && %s; popd)" %(sp_dir, awk_cmd) # run command in sp_dir
    try_cmd(cmd)
    
    t_awk_end = time.time()
    dt = t_awk_end - t_awk_start
    return dt

def run_mod_index(work_dir, basename):
    """
    Calculates the modulation index using the Laura Spitler method.
    """
    print("Calculating modulation index...\n")
    
    t_mi_start = time.time()
    
    combine_sp_files(work_dir, basename)
    
    mi_exec = params.palfa_mi
    combined_file = work_dir + "/single_pulse/" + "%s_MF.sp" %(basename)
    masked_data_file = "raw_data_with_mask.fits"
    output_file = "%s_MF.mi" %(basename)
    
    cmd = "%s %s %s %s" %(mi_exec, combined_file, masked_data_file, output_file)
    try_cmd(cmd)
    
    t_mi_end = time.time()
    dt = t_mi_end - t_mi_start
    return dt

def search_beam(fitsname, fits_dir, work_dir):
    tt = Timer()
    t_start = time.time()
    
    print("Results Directory: %s\n" %work_dir)
    print("FITS Directory: %s\n" %fits_dir)
    print("File Prefix: %s\n" %fitsname)
    
    # Check to see if results directory exists. If not, create it.
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    
    # If selected, do combine_mocks first
    if params.do_combine_mocks:
        tt.combine_mocks = run_combine_mocks(params.combinefile1, params.combinefile2,
            fitsname, fits_dir)
    
    # Check dependencies for planned processing steps.
    check_dependencies(work_dir, fits_dir, fitsname)
    
    # Copy over param file if so desired.
    if params.do_param_cp:
        cp_cmd = 'cp params.py %s/params.txt' %work_dir
        try_cmd(cp_cmd)
    
    # Combine mocks - here?
    # TODO
    
    # If we haven't done so already, go to results directory
    os.chdir(work_dir)
    
    # Need the following if we are doing rfifind or prepsubband
    if params.do_rfifind or params.do_prepsub:
        fitslist = glob('%s/%s*.fits' %(fits_dir, fitsname))
        fitslist.sort()
        #fitsfiles = ' '.join(fitsfiles_arr)
    
    # Run rfifind on the .fits files and put rfifind products in a 
    # folder called rfi_products
    if params.do_rfifind:
        tt.rfifind = run_rfifind(fitslist, fitsname, work_dir)
    rfi_dir = work_dir+'/rfi_products'
    if os.path.exists(rfi_dir):
        maskname = glob(rfi_dir+'/*.mask')[0]
    
    # Run prepsubband on the .fits files
    if params.do_prepsub:
        if params.dmcalls > 1:
            tt.prepsubband = multi_call_prepsubband(fitsname, maskname, fitslist)
        else:
            tt.prepsubband = run_prepsubband(fitsname, maskname, fitslist)
    
    # Run realfft on the dedispersed time series, if selected
    if params.do_fft:
        tt.realfft = run_realfft(work_dir, fitsname)
    
    # Search dedispersed time series for pulsar candidates
    # This includes an acceleration search
    if params.do_candsearch:
        tt.accelsearch = run_accelsearch(work_dir, fitsname)
    
    # Do a single pulse search and move the results into
    # a singlepulse directory
    if params.do_presto_sp:
        tt.presto_sp = run_singlepulse_search(work_dir)
    
    # Create the masked dynamic spectrum
    if params.do_mod_index:
        # Use correct fitsname
        if params.do_combine_mocks:
            tt.mod_index = run_maskdata(maskname, fitsname + "_0001")
        else:
            tt.mod_index = run_maskdata(maskname, fitsname)
    
    # Calculate the modulation index
    if params.do_mod_index:
        tt.mod_index += run_mod_index(work_dir, fitsname)
    
    # Create the plots
    if params.do_make_plots:
        if params.do_plot_color:
            make_plots.make_avg_plot(params.filfile, params.tstart, params.tread, params.dt, make_plots.freqs, 
                params.avg_chan, params.avg_samp, params.dm0, 
                vmin=6, vmax=7)
        if params.do_plot_grey:
            make_plots.make_grey_avg_plot(params.filfile, params.tstart, params.tread, params.dt, make_plots.freqs, 
                params.avg_chan, params.avg_samp, params.dm0, 
                vmin=6, vmax=7)
        if params.do_plot_reverse:
            make_plots.make_reverse_grey_avg_plot(params.filfile, params.tstart, params.tread, params.dt, make_plots.freqs, 
                params.avg_chan, params.avg_samp, params.dm0, 
                vmin=6, vmax=7)
    
    # Finish up time profiling and print summary to screen
    t_finish = time.time()
    tt.total = t_finish - t_start
    tt.print_summary()
    tt.write_summary("%s.log" %fitsname)

    return


####################
##     MAIN       ##
####################


if __name__ == "__main__":

    search_dir = params.search_dir
    basename = params.basename
    fits_dir = params.fits_dir
    search_beam(basename, fits_dir, search_dir)


