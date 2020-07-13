import bisect, os, sys, getopt, infodata, glob
import scipy, scipy.signal, ppgplot, scipy.special
import numpy as Num
from presto import rfft
from psr_utils import coord_to_string
from optparse import OptionParser
from Pgplot import *
import pulsarutil as plsr
import numpy.ma as ma

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

class clust_cand:
    def __init__(self, DM, sigma_max, time_max, bin_max, nsamp, block, sig, mean, \
                 sigma_mean, time_mean, bin_mean, time_ctr, bin_ctr, wtot):
        self.DM = DM
        self.sigma = sigma_max
        self.time = time_max
        self.bin = bin_max
        self.nsamp= nsamp
        self.block = block
        self.sig = sig
        self.mean = mean
        self.sigma_mean = sigma_mean
        self.time_mean = time_mean
        self.bin_mean = bin_mean
        self.time_ctr = time_ctr
        self.bin_ctr = bin_ctr
        self.wtot = wtot
    def __str__(self):
        return "%7.2f %7.2f %13.6f %10d  %3d %3d %3.2f %5.2f %7.2f %13.6f %10d %13.6f %10d %5d\n"%\
               (self.DM, self.sigma_mean, self.time_ctr, self.bin_ctr, self.wtot, \
                  self.block, self.sig, self.mean, 
                  self.sigma, self.time, self.bin, \
                  self.time_mean, self.bin_mean, self.nsamp)
    def __cmp__(self, other):
    # Sort by time (i.e. bin) by default)
        return cmp(self.bin, other.bin)

def cmp_sigma(self, other):
    #Comparison function to sort candidates by significance
    retval = -cmp(self.sigma, other.sigma)
    return retval

def fft_convolve(fftd_data, fftd_kern, lo, hi):
    """
    fft_convolve(fftd_data, fftd_kern, lo, hi):
        Perform a convolution with the complex floating point vectors
            'fftd_data' and 'fftd_kern'.  The returned vector will start at
            at bin 'lo' (must be an integer), and go up to but not
            include bin 'hi' (also an integer).
    """
    # Note:  The initial FFTs should be done like:
    # fftd_kern = rfft(kernel, -1)
    # fftd_data = rfft(data, -1)
    prod = Num.multiply(fftd_data, fftd_kern)
    prod.real[0] = fftd_kern.real[0] * fftd_data.real[0]
    prod.imag[0] = fftd_kern.imag[0] * fftd_data.imag[0]
    return rfft(prod, 1)[lo:hi].astype(Num.float32)

def make_fftd_kerns(downfacts, fftlen):
    fftd_kerns = []
    for downfact in downfacts:
        kern = Num.zeros(fftlen, dtype=Num.float32)
        # These offsets produce kernels that give results
        # equal to scipy.signal.convolve
        if downfact % 2:  # Odd number
            kern[:downfact/2+1] += 1.0
            kern[-(downfact/2):] += 1.0
        else:             # Even number
            kern[:downfact/2+1] += 1.0
            if (downfact > 2):
                kern[-(downfact/2-1):] += 1.0
        # The following normalization preserves the
        # RMS=1 characteristic of the data
        fftd_kerns.append(rfft(kern / Num.sqrt(downfact), -1))
    return fftd_kerns

def prune_related1(hibins, hivals, downfact):
    # Remove candidates that are close to other candidates
    # but less significant.  This one works on the raw 
    # candidate arrays and uses the single downfact
    # that they were selected with.
    toremove = set()
    for ii in range(0, len(hibins)-1):
        if ii in toremove:  continue
        xbin, xsigma = hibins[ii], hivals[ii]
        for jj in range(ii+1, len(hibins)):
            ybin, ysigma = hibins[jj], hivals[jj]
            if (abs(ybin-xbin) > downfact/2):
#            if (abs(ybin-xbin) > downfact):
                break
            else:
                if jj in toremove:
                    continue
                if (xsigma > ysigma):
                    toremove.add(jj)
                else:
                    toremove.add(ii)
    # Now zap them starting from the end
    toremove = sorted(toremove, reverse=True)
    for bin in toremove:
        del(hibins[bin])
        del(hivals[bin])
    return hibins, hivals
    
def prune_related2(dm_candlist, downfacts):
    # Remove candidates that are close to other candidates
    # but less significant.  This one works on the candidate 
    # instances and looks at the different downfacts of the
    # the different candidates.
    toremove = set()
    for ii in range(0, len(dm_candlist)-1):
        if ii in toremove:  continue
        xx = dm_candlist[ii]
        xbin, xsigma = xx.bin, xx.sigma
        for jj in range(ii+1, len(dm_candlist)):
            yy = dm_candlist[jj]
            ybin, ysigma = yy.bin, yy.sigma
            if (abs(ybin-xbin) > max(downfacts)/2):
                break
            else:
                if jj in toremove:
                    continue
                prox = max([xx.downfact/2, yy.downfact/2, 1])
#                prox = max([xx.downfact/2+yy.downfact/2, 1])
                if (abs(ybin-xbin) <= prox):
                    if (xsigma > ysigma):
                        toremove.add(jj)
                    else:
                        toremove.add(ii)
    # Now zap them starting from the end
    toremove = sorted(toremove, reverse=True)
    for bin in toremove:
        del(dm_candlist[bin])
    return dm_candlist

def prune_related3(ts, overthr, nbin=2):
        '''Implementation of cluster algorithm used in place of
         prune_related1 for efficency (LGS).
         ts = times series 
         overthr = samples in ts that are over threshold
         nbin = maximum allowed difference in bins (default 2)
         '''

        # If ts and overthr empty lists, just give them back
        if len(overthr) == 0: return ts, overthr

        #Make local copies
        tstmp=Num.copy(ts)
        overthr=Num.array(overthr)
        overthr=Num.cast['int'](overthr)

        #Define clusters
        #Calculate index where each cluster ends
        cl_end=Num.where(overthr[1:]-overthr[:-1] > nbin)[0]
        #Append last index to include trailing events
        cl_end=Num.append(cl_end, len(overthr)-1)

        p=0
        params=Num.zeros((len(cl_end),2))

        #Loop through clusters and calculate statistics 
        for i in range(len(cl_end)):
                #Define cluster for this loop
                ot=overthr[p:cl_end[i]+1]
                clust=ts[ot]

                nsamp=len(clust)
                cwid=ot[-1]-ot[0]

                smax=overthr[p]+clust.argmax()
                amax=Num.max(clust)

                params[i:]=smax,amax

                p=cl_end[i]+1
        return params.transpose()

def prune_border_cases(dm_candlist, offregions):
    # Ignore those that are locate in a half-width
    # of the boundary between data and padding
    #print offregions
    toremove = set()
    for ii in range(len(dm_candlist))[::-1]:
        cand = dm_candlist[ii]
        loside = cand.bin-cand.downfact/2
        hiside = cand.bin+cand.downfact/2
        if hiside < offregions[0][0]: break
        for off, on in offregions:
            if (hiside > off and loside < on):
                toremove.add(ii)
    # Now zap them starting from the end
    toremove = sorted(toremove, reverse=True)
    for ii in toremove:
        del(dm_candlist[ii])
    return dm_candlist

full_usage = """
usage:  single_pulse_search.py [options] .dat files _or_ .singlepulse files
  [-h, --help]        : Display this help
  [-m, --maxwidth]    : Set the max downsampling in sec (see below for default)
  [-p, --noplot]      : Look for pulses but do not generate a plot
  [-t, --threshold]   : Set a different threshold SNR (default=5.0)
  [-x, --xwin]        : Don't make a postscript plot, just use an X-window
  [-s, --start]       : Only plot events occuring after this time (s)
  [-e, --end]         : Only plot events occuring before this time (s)
  [-g, --glob]        : Use the files from these glob expressions (in quotes)
  [-f, --fast]        : Use a less-accurate but much faster method of detrending
  Perform a single-pulse search (or simply re-plot the results of a
  single-pulse search) on a set of de-dispersed time series (.dat
  files).
  The search attempts to find pulses by matched-filtering the data
  with a series of different width boxcar functions.  The possible
  boxcar sizes are [1, 2, 3, 4, 6, 9, 14, 20, 30, 45, 70, 100, 150]
  bins.  By default the boxcars <= 30 are used.  You can specify
  that the larger boxcars are used with the -m (or --maxwidth) option.
  The matched filtering (and accounting for all the possible 'phase'
  offsets of each boxcar) is accomplished by convolving the boxcars
  with the full resolution data.  'Duplicate' candidates from this
  process are filtered, leaving only the most significant.  The time
  series are initially smoothed using a piecewise linear fit to the
  data where each piece is 2000 data points long.
  If the input files are .singlepulse files, we won't actually perform
  a search, we'll only read in the output .singlepulse files and make
  a plot using the information they contain (along with the
  corresponding .inf files).
  Copyright Scott Ransom <sransom@nrao.edu>, 2005
"""
usage = "usage: %prog [options] .dat files _or_ .singlepulse files"
    
def read_singlepulse_files(infiles, threshold, T_start, T_end):
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
                cands = Num.loadtxt(infile)
                if len(cands.shape)==1:
                    cands = Num.asarray([cands])
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

def clean_timeseries(ts, clust_len=4, nabove=10.0, debug=False):
    '''Attempts to clean a time series to get reliable
    calculation of mean and std.
    It applies a threshold and looks for greater than
    length clust_len and takes out a region surrounding it
    Inputs:
    ts = time series
    thr = SNR multiplier for threshold
    clust_len = the minimum length assumed for a cluster
    debug = will additionally return masked time series
    Outputs:
    tmean = cleaned mean of time series
    tsig = cleaned standard deviation of time series
    '''
    nloops=0

    #Copy time series array and make it a masked array
    tstmp=Num.copy(ts)

    #Calc threshold
    thr=Num.sqrt(2)*scipy.special.erfinv((1.0-nabove/len(tstmp)))

    #Calulate statistics and apply threshold
    ts_mean,ts_sig,ts_med=Num.mean(tstmp),Num.std(tstmp),Num.median(tstmp)
    ot=Num.where(Num.abs(tstmp-ts_med) < thr*ts_sig)[0]
    ot_len=len(ot)
    ot_diff=len(tstmp)-ot_len

    if Num.round(ts_sig, decimals=1)==0.0: rmszero=1
    else: rmszero=0

    if debug==True: print "Initial stats: ", ts_mean, ts_med, ts_sig, thr, ot_len
    if debug==True: print Num.where((tstmp-ts_med) > thr*ts_sig)[0]

    #Loop until sufficiently clean
    while ot_diff >= nabove and nloops<6 and ts_sig>0.0:
        if rmszero==1: break

        ts_mean,ts_sig,ts_med=Num.mean(tstmp[ot]),Num.std(tstmp[ot]),Num.median(tstmp[ot])

        try:
            thr=Num.sqrt(2)*scipy.special.erfinv((1.0-nabove/len(tstmp[ot])))
        except ZeroDivisionError:
            print "ZeroDivisionError in scipy.special.erfinv()"
            thr=Num.sqrt(2)*scipy.special.erfinv((1.0-nabove/len(tstmp)))

        ot=Num.where(Num.abs(tstmp-ts_med) < thr*ts_sig)[0]
        ot_diff=ot_len-len(ot)
        ot_len=len(ot)
        if debug==True: print "Loop number ", nloops, ts_mean, ts_med, ts_sig, thr, ot_len
        nloops+=1
    
    if Num.round(ts_sig, decimals=1)==0.0: rmszero=1
    else: rmszero=0

    if rmszero != 1:
        try:
            thr=Num.sqrt(2)*scipy.special.erfinv((1.0-nabove/len(tstmp[ot])))
        except ZeroDivisionError:
            print "ZeroDivisionError in scipy.special.erfinv()"
            thr=Num.sqrt(2)*scipy.special.erfinv((1.0-nabove/len(tstmp)))

        ot_good=Num.copy(ot)
        ot=Num.where(tstmp-ts_med > thr*ts_sig)[0]

        #Define where clusters end
        cl_end=Num.where(ot[1:]-ot[:-1] > 8)[0]
        cl_end=Num.append(cl_end, len(ot)-1)

        ot_bad=Num.array([])
        p=0
        for i in range(len(cl_end)):
            clust=ts[ot[p:cl_end[i]+1]]
            clen=len(clust)

            if debug==True: print p, cl_end[i]+1, ot[p:cl_end[i]+1]
            #If a cluster is sufficently broad, define a region
            #25% larger than the cluster and mask it as bad
            if clen > 1:
                off=max(1,clen/4)
                slo=max(ot[p]-off, 0)
                shi=min(ot[cl_end[i]]+off, len(ts))
                ot_bad=Num.append(ot_bad, Num.arange(slo,shi))
                if debug==True: print "ot_bad:", ot_bad

            p=cl_end[i]+1

        ot_good=Num.delete(ot_good, ot_bad)
        ts_mean,ts_sig=Num.mean(ts[ot_good]),Num.std(ts[ot_good])

    return ts_mean,ts_sig

def clean_timeseries_old(ts, thr, clust_len=4, debug=False):
    '''Attempts to clean a time series to get reliable
    calculation of mean and std.
    It applies a threshold and looks for greater than
    length clust_len and takes out a region surrounding it
    Inputs:
    ts = time series
    thr = SNR multiplier for threshold
    clust_len = the minimum length assumed for a cluster
    debug = will additionally return masked time series
    Outputs:
    tmean = cleaned mean of time series
    tsig = cleaned standard deviation of time series
    '''
    nloops=0

    #Copy time series array and make it a masked array
    ts_mask=ma.copy(ts)

    #Calulate statistics and apply threshold
    ts_mean,ts_sig=Num.mean(ts_mask),Num.std(ts_mask)
    ot=Num.where((ts_mask-ts_mean) > thr*ts_sig)[0]

    #Define where clusters end
    cl_end=Num.where(ot[1:]-ot[:-1] > 2)[0]
    cl_end=Num.append(cl_end, len(ot)-1)

    if debug==True: 
        print "First std: %f Num bad: %d" % (ts_sig, len(ot))
        print ot

    #Loop until sufficiently clean
    while nloops<6:
        if Num.round(ts_sig, decimals=1)==0.0: break
        #Loop over clusters
        p=0
        for i in range(len(cl_end)):
            clust=ts[ot[p:cl_end[i]+1]]
            clen=len(clust)

            if debug==True: print p, cl_end[i]+1, ot[p:cl_end[i]+1]
            #If a cluster is sufficently broad, define a region
            #25% larger than the cluster and mask it as bad
            if clen > clust_len:
                off=clen/4
                slo=max(ot[p]-off, 0)
                shi=min(ot[cl_end[i]]+off, len(ts))
                ts_mask[slo:shi]=ma.masked
            #Otherwise just mask the high values 
            else: 
                ts_mask[p:cl_end[i]+1]=ma.masked
            p=cl_end[i]+1

        #Recalculate statistics
        if debug==True: print "New: %f\n" % Num.std(ts_mask.data)
        if debug==True: print ts_mask.mask
        ts_mean_new,ts_sig_new=Num.mean(ts_mask),Num.std(ts_mask)

        #See the stats are clean enough
        if ts_sig/ts_sig_new - 1.0 < 0.05:
            if debug==True: print "Clean"
            break
        else: 
            if debug==True: print ts_sig,ts_sig_new
            ts_sig,ts_mean=ts_sig_new,ts_mean_new
            ot=Num.where((ts_mask.data-ts_mean) > thr*ts_sig)[0]
            cl_end=Num.where(ot[1:]-ot[:-1] > 2)[0]
            cl_end=Num.append(cl_end, len(ot)-1)

        nloops+=1

    return ts_mean,ts_sig

def clean_stddev(ts, thr,  verbose=False):
        # Finds a "clean" std deviation by masking
        # outliers until the change in std dev
        # is less than about 1%
        #ts = time series
        #thr = multiplier of std dev for thresholding
        #verbose = report mean, std deviation, ratio for each inter

        nloops=0

        #Make local copy of ts to clean 
        tstmp=ma.copy(ts)

        #Calculate statistics of uncleaned data
        sigold=Num.std(tstmp)
        tsmean=Num.mean(tstmp)

        if Num.round(sigold, decimals=1) == 0.0: return sigold
        #return tsmean, sigold

        #Do first clean stage
        inds=ma.where(tstmp - tsmean > thr*sigold)[0]
#        inds=ma.where(tstmp  > thr*sigold)[0]

        #If there's nothing to clean, just leave (for efficiency)
        if len(inds) == 0: return sigold
        #return tsmean, sigold

        tstmp[inds]=ma.masked
        sig=Num.std(tstmp)
        tsmean=Num.mean(tstmp)

#        inds=Num.where(tstmp-tsmean < -1*(thr)*sig)[0]
#        tstmp[inds]=ma.masked
#        sig=Num.std(tstmp)
#        tsmean=Num.mean(tstmp)

        if Num.round(sig, decimals=1) == 0.0: return sig
        #return Num.tsmean,sig

#        if verbose == True: print mold, sigold
#        if verbose == True: print len(inds)
#        if verbose == True: print m, sig, sigold/sig-1.0

        #Loop through cleaning stages until ratio of 
        #  current stddev is less than 1 % the previous
        while nloops<6:
            if sigold/sig - 1.0 < 0.01: break

            inds=ma.where(tstmp - tsmean > thr*sig)[0]
#            inds=ma.where(tstmp > thr*sig)[0]
            tstmp[inds]=ma.masked

            sigold=sig
            sig=Num.std(tstmp)
            tsmean=Num.mean(tstmp)

            nloops+=1
            if verbose==True: print nloops 

#        return tsmean,sigold
        return sigold

def downsample_factor(dm, max=False):
    '''Return the downsample factor for a given
    DM for a fixed PRESTO DDplan
    Currently assumes PALFA Mock data
    Input:
    dm = dispersion measure
    max = If true, return max downsamle regardless of input dm
        (default False)
    Output:
    ds = downsample factor
    '''

    dm_boundaries=Num.array([212.8, 443.2, 534.4, 876.4, 990.4, 1750.4, 2038.4])
    downsample=Num.array([1, 2, 3, 5, 6, 10, 15])

    tmp=Num.where(dm < dm_boundaries)[0]
    ds = downsample[min(tmp)] 

    if max==True: ds = downsample[-1]

    return ds 

def hist_sigma(data, blo=0, bhi=120, bstep=1):
    
    bins=range(blo, bhi+1, bstep)
   
    hist,hb=Num.histogram(data, bins=bins, range=(min(bins),max(bins)))
    
    total=Num.sum(hist)
    
    count=Num.max(hist)
    arg=hist.argmax()
    nbin=1
    offset=1
    left=0
    
    while count<total/3:
        if left==0: count+=hist[arg+offset]
        else: count+=hist[arg-offset]
        nbin+=1
        if left==0: left=1
        else: offset+=1

    return bstep*nbin

def flag_last_chunk(bad_blocks, detrendlen, chunklen):

    inds=Num.where(bad_blocks[1:]-bad_blocks[:-1] != 1)[0]

    if len(inds)==0:
        firstbad=bad_blocks[0]
        loc=0
    else:
        firstbad=bad_blocks[inds[-1]+1]
        loc=inds[-1]

    ol=(firstbad*detrendlen) % chunklen
    n2add=ol/detrendlen

    new=Num.arange(-1*n2add, 0, 1)+firstbad
    bad_blocks=Num.insert(bad_blocks, loc*Num.ones(n2add)+1, new)

    print "New bad block: ", new
    return bad_blocks

def main():
    parser = OptionParser(usage)
    parser.add_option("-x", "--xwin", action="store_true", dest="xwin",
                      default=False, help="Don't make a postscript plot, just use an X-window")
    parser.add_option("-p", "--noplot", action="store_false", dest="makeplot",
                      default=True, help="Look for pulses but do not generate a plot")
    parser.add_option("-m", "--maxwidth", type="float", dest="maxwidth", default=0.0,
                      help="Set the max downsampling in sec (see below for default)")
    parser.add_option("-t", "--threshold", type="float", dest="threshold", default=5.0,
                      help="Set a different threshold SNR (default=5.0)")
    parser.add_option("-s", "--start", type="float", dest="T_start", default=0.0,
                      help="Only plot events occuring after this time (s)")
    parser.add_option("-e", "--end", type="float", dest="T_end", default=1e9,
                      help="Only plot events occuring before this time (s)")
    parser.add_option("-g", "--glob", type="string", dest="globexp", default=None,
                      help="Process the files from this glob expression")
    parser.add_option("-f", "--fast", action="store_true", dest="fast",
                      default=False, help="Use a faster method of de-trending (2x speedup)")
    parser.add_option("-i", "--iter", action="store_true", dest="iter",
                      default=False, help="Use iterative cleaning for stats calc")
    parser.add_option("-c", "--clust", action="store_true", dest="doclust",
                      default=False, help="Also apply cluster algorithm")
    parser.add_option("-w", "--clust_maxgap", type="int", dest="maxgap", default=1,
                      help="Set the maximum gap (in bins) for clustering")
    parser.add_option("-r", "--noflag", action="store_true", dest="noflag",
                      default=False, help="Do not do any RFI flagging")
    (opts, args) = parser.parse_args()
    if len(args)==0:
        if opts.globexp==None:
            print full_usage
            sys.exit(0)
        else:
            args = []
            for globexp in opts.globexp.split():
                args += glob.glob(globexp)
    useffts = True
    dosearch = True
    if opts.xwin:
        pgplot_device = "/XWIN"
    else:
        pgplot_device = ""

#    fftlen = 8192     # Should be a power-of-two for best speed
#    chunklen = 8000   # Must be at least max_downfact less than fftlen
#    detrendlen = 1000 # length of a linear piecewise chunk of data for detrending
    fftlen = 65536 # Should be a power-of-two for best speed
    chunklen = 64000   # Must be at least max_downfact less than fftlen
    detrendlen = 4000 # length of a linear piecewise chunk of data for detrending
    blocks_per_chunk = chunklen / detrendlen
    overlap = (fftlen - chunklen)/2
    worklen = chunklen + 2*overlap  # currently it is fftlen...

    max_downfact = 30
    #LGS: Expanded to include 300, 1000 and 1500
    default_downfacts = [2, 3, 4, 6, 9, 14, 20, 30, 45, 70, 100, 150,  300, 500, 1000, 1500]
#    default_downfacts = [2, 3, 4, 6, 9, 14, 20, 30, 45, 70, 100, 150]

    if args[0].endswith(".singlepulse"):
        filenmbase = args[0][:args[0].rfind(".singlepulse")]
        dosearch = False
    elif args[0].endswith(".cluster"):
        filenmbase = args[0][:args[0].rfind(".cluster")]
        dosearch = False
    elif args[0].endswith(".dat"):
        filenmbase = args[0][:args[0].rfind(".dat")]
    else:
        filenmbase = args[0]

    # Don't do a search, just read results and plot
    if not dosearch:
        info, DMs, candlist, num_v_DMstr = \
              read_singlepulse_files(args, opts.threshold, opts.T_start, opts.T_end)
        orig_N, orig_dt = int(info.N), info.dt
        obstime = orig_N * orig_dt
    else:
        DMs = []
        candlist = []
        num_v_DMstr = {}

        # Loop over the input files
        for filenm in args:
            if filenm.endswith(".dat"):
                filenmbase = filenm[:filenm.rfind(".dat")]
            else:
                filenmbase = filenm
            info = infodata.infodata(filenmbase+".inf")
            DMstr = "%.2f"%info.DM
            DMs.append(info.DM)
            N, dt = int(info.N), info.dt
            obstime = N * dt
            dsfact=downsample_factor(info.DM)
            # Choose the maximum width to search based on time instead
            # of bins.  This helps prevent increased S/N when the downsampling
            # changes as the DM gets larger.
            if opts.maxwidth > 0.0:
                downfacts = [x for x in default_downfacts if x*dt <= opts.maxwidth]
            else:
                downfacts = [x for x in default_downfacts if x <= max_downfact]
            if len(downfacts) == 0:
                downfacts = [default_downfacts[0]]
            if (filenm == args[0]):
                orig_N = N
                orig_dt = dt
                if useffts:
                    fftd_kerns = make_fftd_kerns(downfacts, fftlen)
            if info.breaks:
                offregions = zip([x[1] for x in info.onoff[:-1]],
                                 [x[0] for x in info.onoff[1:]])
            outfile = open(filenmbase+'.singlepulse', mode='w')
            if opts.doclust: outclust = open(filenmbase+'.cluster', mode='w')

            # Compute the file length in detrendlens
            roundN = N/detrendlen * detrendlen
            numchunks = roundN / chunklen
            # Read in the file
            print 'Reading "%s"...'%filenm
            timeseries = Num.fromfile(filenm, dtype=Num.float32, count=roundN)
            # Split the timeseries into chunks for detrending
            numblocks = roundN/detrendlen
            timeseries.shape = (numblocks, detrendlen)
            stds = Num.zeros(numblocks, dtype=Num.float64)
            stds_orig = Num.zeros(numblocks, dtype=Num.float64)
            means = Num.zeros(numblocks, dtype=Num.float64)
            # de-trend the data one chunk at a time
            print '  De-trending the data and computing statistics...'
            for ii, chunk in enumerate(timeseries):
                if opts.fast:  # use median removal instead of detrending (2x speedup)
                    tmpchunk = chunk.copy()
                    tmpchunk.sort()
                    med = tmpchunk[detrendlen/2]
                    chunk -= med
                    tmpchunk -= med
                elif opts.iter:
#                     ot,tsig,tmean=plsr.threshold(chunk, 3.0)
                     tmean,tsig=clean_timeseries(chunk,nabove=10.0,debug=False)
                     chunk -= tmean
                     tmpchunk = chunk.copy() 
                else:
                    # The detrend calls are the most expensive in the program
                    timeseries[ii] = scipy.signal.detrend(chunk, type='linear')
                    tmpchunk = timeseries[ii].copy()
                    tmpchunk.sort()
                # The following gets rid of (hopefully) most of the 
                # outlying values (i.e. power dropouts and single pulses)
                # If you throw out 5% (2.5% at bottom and 2.5% at top)
                # of random gaussian deviates, the measured stdev is ~0.871
                # of the true stdev.  Thus the 1.0/0.871=1.148 correction below.
                # The following is roughly .std() since we already removed the median
                stds[ii] = Num.sqrt((tmpchunk[detrendlen/40:-detrendlen/40]**2.0).sum() /
                                    (0.95*detrendlen))
                if opts.iter:
                    means[ii] = tmean
                    stds_orig[ii] = tsig
                else:
                    means[ii]=0.0
                    stds_orig[ii] = stds[ii]
            if opts.noflag: 
                median_stds = Num.nanmedian(stds_orig)
                std_stds = hist_sigma(stds_orig) # stddev of stddevs of chunks
                lo_std = max(median_stds - 3.1*std_stds, 0)
                hi_std = median_stds + 10.0*std_stds
                all_bad = Num.where((stds_orig <= lo_std) | (stds_orig > hi_std))[0]
                lo_bad = Num.where(stds_orig <= lo_std)[0]
                bad_blocks=all_bad
#                bad_blocks=lo_bad
                bad_blocks=flag_last_chunk(bad_blocks, detrendlen, chunklen)
            else: 
                # Determine a list of "bad" chunks.  We will not search these.
                # LGS: If --noflag option is given, will only ignore blocks with low std
                # (this nicely flags padding at end of time series)
                #   Otherwise it will flag both anomolously high and lo blocks (default)
                # Blocks with anomoulously high or low stds will have their std replaced
                #  with the median value

                stds *= 1.148
                # sort the standard deviations and separate those with
                # very low or very high values
                sort_stds = stds.copy()
                sort_stds.sort()
                # identify the differences with the larges values (this
                # will split off the chunks with very low and very high stds
                locut = (sort_stds[1:numblocks/2+1] -
                         sort_stds[:numblocks/2]).argmax() + 1
                hicut = (sort_stds[numblocks/2+1:] -
                         sort_stds[numblocks/2:-1]).argmax() + numblocks/2 - 2
                std_stds = scipy.std(sort_stds[locut:hicut])
                median_stds = sort_stds[(locut+hicut)/2]
                lo_std = median_stds - 4.0 * std_stds
                hi_std = median_stds + 4.0 * std_stds
                bad_blocks = Num.nonzero((stds < lo_std) | (stds > hi_std))[0]
            print "    pseudo-median block standard deviation = %.2f" % (median_stds)
            print "    identified %d bad blocks out of %d (i.e. %.2f%%)" % \
                  (len(bad_blocks), len(stds),
                   100.0*float(len(bad_blocks))/float(len(stds)))
            print " High and low stds: %.2f  %.2f" % (hi_std, lo_std)
            print " Downsample factor: %d " % dsfact
            print "  Now searching..."
            print bad_blocks

            stds[bad_blocks] = median_stds
            # Now normalize all of the data and reshape it to 1-D
            if opts.iter:
                timeseries /= stds_orig[:,Num.newaxis]
            else:
                timeseries /= stds[:,Num.newaxis]

            timeseries.shape = (roundN,)
            # And set the data in the bad blocks to zeros
            # Even though we don't search these parts, it is important
            # because of the overlaps for the convolutions
            for bad_block in bad_blocks:
                loind, hiind = bad_block*detrendlen, (bad_block+1)*detrendlen
                timeseries[loind:hiind] = 0.0
            # Convert to a set for faster lookups below
            bad_blocks = set(bad_blocks)

            # Step through the data
            dm_candlist = []
            if opts.doclust: cand_clust = []
            for chunknum in range(numchunks):
                loind = chunknum*chunklen-overlap
                hiind = (chunknum+1)*chunklen+overlap
                # Take care of beginning and end of file overlap issues
                if (chunknum==0): # Beginning of file
                    chunk = Num.zeros(worklen, dtype=Num.float32)
                    chunk[overlap:] = timeseries[loind+overlap:hiind]
                elif (chunknum==numchunks-1): # end of the timeseries
                    chunk = Num.zeros(worklen, dtype=Num.float32)
                    chunk[:-overlap] = timeseries[loind:hiind-overlap]
                else:
                    chunk = timeseries[loind:hiind]

                # Make a set with the current block numbers
                lowblock = blocks_per_chunk * chunknum
                currentblocks = set(Num.arange(blocks_per_chunk) + lowblock)
                localgoodblocks = Num.asarray(list(currentblocks -
                                                   bad_blocks)) - lowblock
                # Search this chunk if it is not all bad
                if len(localgoodblocks):
                    # This is the good part of the data (end effects removed)
                    goodchunk = chunk[overlap:-overlap]

                    # need to pass blocks/chunklen, localgoodblocks
                    # dm_candlist, dt, opts.threshold to cython routine

                    # Search non-downsampled data first
                    # NOTE:  these nonzero() calls are some of the most
                    #        expensive calls in the program.  Best bet would 
                    #        probably be to simply iterate over the goodchunk
                    #        in C and append to the candlist there.
                    hibins = Num.flatnonzero(goodchunk>opts.threshold)
                    hivals = goodchunk[hibins]
                    hibloc = Num.copy(hibins)
                    hibins += chunknum * chunklen
                    hiblocks = hibins/detrendlen
                    # Add the candidates (which are sorted by bin)
                    for bin, val, block in zip(hibins, hivals, hiblocks):
                        if block not in bad_blocks:
                            time = bin * dt
                            dm_candlist.append(candidate(info.DM, val, time, bin, 1, \
                                block, stds_orig[block], means[block]))
                    #Perform cluster algorithm
                    if opts.doclust and len(hibloc) != 0:
                        nsamp,smax,amax,smean,amean,wgp,sctr=plsr.cluster(goodchunk, hibloc, nbin=opts.maxgap)
                        amean=Num.sqrt(nsamp)*amean
                        smax += chunknum*chunklen
                        smean += chunknum*chunklen
                        sctr += chunknum*chunklen
                        tmax,tmean,tctr = smax*dt, smean*dt, sctr*dt
                        for ii in range(len(nsamp)):
                            tmpblk=int(sctr[ii])/detrendlen
                            if tmpblk in bad_blocks: continue

                            cand_clust.append(clust_cand(info.DM, amax[ii], tmax[ii], smax[ii],\
                                nsamp[ii], tmpblk, stds_orig[tmpblk], means[tmpblk], amean[ii], \
                                tmean[ii], smean[ii], tctr[ii], sctr[ii], wgp[ii]))

                    # Prepare our data for the convolution
                    if useffts: fftd_chunk = rfft(chunk, -1)

                    # Now do the downsampling...
                    for ii, downfact in enumerate(downfacts):
                        if useffts: 
                            # Note:  FFT convolution is faster for _all_ downfacts, even 2
                            goodchunk = fft_convolve(fftd_chunk, fftd_kerns[ii],
                                                     overlap, -overlap)
                        else:
                            # The normalization of this kernel keeps the post-smoothing RMS = 1
                            kernel = Num.ones(downfact, dtype=Num.float32) / \
                                     Num.sqrt(downfact)
                            smoothed_chunk = scipy.signal.convolve(chunk, kernel, 1)
                            goodchunk = smoothed_chunk[overlap:-overlap]
                        #Calculate a cleaned std dev of the convolved timeseries
                        #Note: sig=4.0 -> prob. of 1 in ~16000
                        loc_std=clean_stddev(goodchunk, 4.0, verbose=False)
                        if loc_std==0.0: loc_std=1000.0
                        goodchunk/=loc_std
                        hibins = Num.flatnonzero(goodchunk>opts.threshold)
                        hivals = goodchunk[hibins]
                        hibins += chunknum * chunklen
                        hiblocks = hibins/detrendlen
                        hibtmp = hibins - chunknum*chunklen
                        hibins = hibins.tolist()
                        hivals = hivals.tolist()
                        hibtmp = hibtmp.tolist()
                        # Now walk through the new candidates and remove those
                        # that are not the highest but are within downfact/2
                        # bins of a higher signal pulse
##                        hibins, hivals = prune_related1(hibins, hivals, downfact)
                        hibins, hivals = prune_related3(goodchunk, hibtmp, downfact)
                        hibins += chunknum*chunklen
                        hiblocks = Num.array(hibins)/detrendlen
                        hiblocks = hiblocks.astype('int')
                        # Insert the new candidates into the candlist, but
                        # keep it sorted...
                        for bin, val, block in zip(hibins, hivals, hiblocks):
                            if block not in bad_blocks:
                                              time=bin * dt
                                              bisect.insort(dm_candlist,
                                              candidate(info.DM, val, time, bin, downfact, \
                                                 block, stds_orig[block], means[block]))

            # Now walk through the dm_candlist and remove the ones that
            # are within the downsample proximity of a higher
            # signal-to-noise pulse
            dm_candlist = prune_related2(dm_candlist, downfacts)
            print "  Found %d pulse candidates"%len(dm_candlist)
            
            # Get rid of those near padding regions
            if info.breaks: prune_border_cases(dm_candlist, offregions)

            # Write the pulses to an ASCII output file
            if len(dm_candlist):
                #dm_candlist.sort(cmp_sigma)
                outfile.write("# DM      Sigma      Time (s)     Sample    Downfact    Block    RMS   Mean\n")
                for cand in dm_candlist:
                    cand.bin=cand.bin*dsfact
                    outfile.write(str(cand))
            outfile.close()

            #Write out cluster results
            if opts.doclust and len(cand_clust):
                outclust.write("# DM    SNRmean    TimeCtr    SampNumCtr    Width   "+ \
                                  "Block    RMS    Mean    SNRMax    TimeMax   " + \
                                  "SampNumMax    TimeMean    SampNumMean    NumSamp\n")
                for cand in cand_clust:
                    cand.bin*=dsfact
                    cand.bin_mean*=dsfact
                    cand.bin_ctr*=dsfact
                    outclust.write(str(cand))
            if opts.doclust: outclust.close()

            # Add these candidates to the overall candidate list
            for cand in dm_candlist:
                candlist.append(cand)
            num_v_DMstr[DMstr] = len(dm_candlist)

    if (opts.makeplot):

        # Step through the candidates to make a SNR list
        DMs.sort()
        snrs = []
        for cand in candlist:
            snrs.append(cand.sigma)
        if snrs:
            maxsnr = max(int(max(snrs)), int(opts.threshold)) + 3
        else:
            maxsnr = int(opts.threshold) + 3

        # Generate the SNR histogram
        snrs = Num.asarray(snrs)
        (num_v_snr, lo_snr, d_snr, num_out_of_range) = \
                    scipy.stats.histogram(snrs,
                                          int(maxsnr-opts.threshold+1),
                                          [opts.threshold, maxsnr])
        snrs = Num.arange(maxsnr-opts.threshold+1, dtype=Num.float64) * d_snr \
               + lo_snr + 0.5*d_snr
        num_v_snr = num_v_snr.astype(Num.float32)
        num_v_snr[num_v_snr==0.0] = 0.001

        # Generate the DM histogram
        num_v_DM = Num.zeros(len(DMs))
        for ii, DM in enumerate(DMs):
            num_v_DM[ii] = num_v_DMstr["%.2f"%DM]
        DMs = Num.asarray(DMs)

        # open the plot device
        short_filenmbase = filenmbase[:filenmbase.find("_DM")]
        if opts.T_end > obstime:
            opts.T_end = obstime
        if pgplot_device:
            ppgplot.pgopen(pgplot_device)
        else:
            if (opts.T_start > 0.0 or opts.T_end < obstime):
                if opts.doclust:
                    ppgplot.pgopen(short_filenmbase+'_%.0f-%.0fs_cluster.ps/VPS'%
                               (opts.T_start, opts.T_end))
                else:
                    ppgplot.pgopen(short_filenmbase+'_%.0f-%.0fs_singlepulse.ps/VPS'%
                               (opts.T_start, opts.T_end))
            else:
                if opts.doclust:
                    ppgplot.pgopen(short_filenmbase+'_cluster.ps/VPS')
                else:
                    ppgplot.pgopen(short_filenmbase+'_singlepulse.ps/VPS')
        ppgplot.pgpap(7.5, 1.0)  # Width in inches, aspect

        # plot the SNR histogram
        ppgplot.pgsvp(0.06, 0.31, 0.6, 0.87)
        ppgplot.pgswin(opts.threshold, maxsnr,
                       Num.log10(0.5), Num.log10(2*max(num_v_snr)))
        ppgplot.pgsch(0.8)
        ppgplot.pgbox("BCNST", 0, 0, "BCLNST", 0, 0)
        ppgplot.pgmtxt('B', 2.5, 0.5, 0.5, "Signal-to-Noise")
        ppgplot.pgmtxt('L', 1.8, 0.5, 0.5, "Number of Pulses")
        ppgplot.pgsch(1.0)
        ppgplot.pgbin(snrs, Num.log10(num_v_snr), 1)

        # plot the DM histogram
        ppgplot.pgsvp(0.39, 0.64, 0.6, 0.87)
        # Add [1] to num_v_DM in YMAX below so that YMIN != YMAX when max(num_v_DM)==0
        ppgplot.pgswin(min(DMs)-0.5, max(DMs)+0.5, 0.0, 1.1*max(num_v_DM+[1]))
        ppgplot.pgsch(0.8)
        ppgplot.pgbox("BCNST", 0, 0, "BCNST", 0, 0)
        ppgplot.pgmtxt('B', 2.5, 0.5, 0.5, "DM (pc cm\u-3\d)")
        ppgplot.pgmtxt('L', 1.8, 0.5, 0.5, "Number of Pulses")
        ppgplot.pgsch(1.0)
        ppgplot.pgbin(DMs, num_v_DM, 1)

        # plot the SNR vs DM plot 
        ppgplot.pgsvp(0.72, 0.97, 0.6, 0.87)
        ppgplot.pgswin(min(DMs)-0.5, max(DMs)+0.5, opts.threshold, maxsnr)
        ppgplot.pgsch(0.8)
        ppgplot.pgbox("BCNST", 0, 0, "BCNST", 0, 0)
        ppgplot.pgmtxt('B', 2.5, 0.5, 0.5, "DM (pc cm\u-3\d)")
        ppgplot.pgmtxt('L', 1.8, 0.5, 0.5, "Signal-to-Noise")
        ppgplot.pgsch(1.0)
        cand_ts = Num.zeros(len(candlist), dtype=Num.float32)
        cand_SNRs = Num.zeros(len(candlist), dtype=Num.float32)
        cand_DMs = Num.zeros(len(candlist), dtype=Num.float32)
        for ii, cand in enumerate(candlist):
            cand_ts[ii], cand_SNRs[ii], cand_DMs[ii] = \
                         cand.time, cand.sigma, cand.DM
        ppgplot.pgpt(cand_DMs, cand_SNRs, 20)

        # plot the DM vs Time plot
        ppgplot.pgsvp(0.06, 0.97, 0.08, 0.52)
        ppgplot.pgswin(opts.T_start, opts.T_end, min(DMs)-0.5, max(DMs)+0.5)
        ppgplot.pgsch(0.8)
        ppgplot.pgbox("BCNST", 0, 0, "BCNST", 0, 0)
        ppgplot.pgmtxt('B', 2.5, 0.5, 0.5, "Time (s)")
        ppgplot.pgmtxt('L', 1.8, 0.5, 0.5, "DM (pc cm\u-3\d)")
        # Circles are symbols 20-26 in increasing order
        snr_range = 12.0
        cand_symbols = (cand_SNRs-opts.threshold)/snr_range * 6.0 + 20.5
        cand_symbols = cand_symbols.astype(Num.int32)
        cand_symbols[cand_symbols>26] = 26
        for ii in [26, 25, 24, 23, 22, 21, 20]:
            inds = Num.nonzero(cand_symbols==ii)[0]
            ppgplot.pgpt(cand_ts[inds], cand_DMs[inds], ii)

        # Now fill the infomation area
        ppgplot.pgsvp(0.05, 0.95, 0.87, 0.97)
        ppgplot.pgsch(1.0)
        ppgplot.pgmtxt('T', 0.5, 0.0, 0.0,
                       "Single pulse results for '%s'"%short_filenmbase)
        ppgplot.pgsch(0.8)
        # first row
        ppgplot.pgmtxt('T', -1.1, 0.02, 0.0, 'Source: %s'%\
                       info.object)
        ppgplot.pgmtxt('T', -1.1, 0.33, 0.0, 'RA (J2000):')
        ppgplot.pgmtxt('T', -1.1, 0.5, 0.0, info.RA)
        ppgplot.pgmtxt('T', -1.1, 0.73, 0.0, 'N samples: %.0f'%orig_N)
        # second row
        ppgplot.pgmtxt('T', -2.4, 0.02, 0.0, 'Telescope: %s'%\
                       info.telescope)
        ppgplot.pgmtxt('T', -2.4, 0.33, 0.0, 'DEC (J2000):')
        ppgplot.pgmtxt('T', -2.4, 0.5, 0.0, info.DEC)
        ppgplot.pgmtxt('T', -2.4, 0.73, 0.0, 'Sampling time: %.2f \gms'%\
                       (orig_dt*1e6))
        # third row
        if info.instrument.find("pigot") >= 0:
            instrument = "Spigot"
        else:
            instrument = info.instrument
        ppgplot.pgmtxt('T', -3.7, 0.02, 0.0, 'Instrument: %s'%instrument)
        if (info.bary):
            ppgplot.pgmtxt('T', -3.7, 0.33, 0.0, 'MJD\dbary\u: %.12f'%info.epoch)
        else:
            ppgplot.pgmtxt('T', -3.7, 0.33, 0.0, 'MJD\dtopo\u: %.12f'%info.epoch)
        ppgplot.pgmtxt('T', -3.7, 0.73, 0.0, 'Freq\dctr\u: %.1f MHz'%\
                       ((info.numchan/2-0.5)*info.chan_width+info.lofreq))
        ppgplot.pgiden()
        ppgplot.pgend()

if __name__ == '__main__':
    if (0):
        # The following is for profiling
        import hotshot
        prof = hotshot.Profile("hotshot_edi_stats")
        prof.runcall(main)
        prof.close()
        # To see the results:
        if (0):
            from hotshot import stats
            s = stats.load("hotshot_edi_stats")
            s.sort_stats("time").print_stats()
    else:
        main()
