# Get the number of samples from a list of data files
# 
# The psrfits header-reading code draws heavily from P. Lazarus'
# psrfits.py code for the PALFA pipeline

from astropy.io import fits
import sigproc
import glob
import numpy as np
import sys
import psr_utils

def psrfits_samp(flist):
    """
    This function reads in multiple .fits files and counts
    how many time samples are in the total observation. There
    are lots of checks and error messages because I just
    copied it from P. Lazarus' psrfits.py code in the PALFA
    pipeline.
    """
    fitslist = flist
    fitslist.sort()
    n_samp = 0
    num_subint   = np.zeros(len(fitslist))
    num_pad      = np.zeros(len(fitslist))
    num_spec     = np.zeros(len(fitslist))
    start_subint = np.zeros(len(fitslist))
    start_spec   = np.zeros(len(fitslist))
    start_MJD    = np.zeros(len(fitslist))
    for ii, fl in enumerate(fitslist):
        hdus = fits.open(fl, mode='readonly')
        print ii, fl
        
        # Go to primary HDU
        primary = hdus['PRIMARY'].header
        start_MJD[ii] = primary['STT_IMJD'] + (primary['STT_SMJD'] + \
                        primary['STT_OFFS'])/psr_utils.SECPERDAY

        # Go to subint HDU
        subint = hdus['SUBINT'].header
        
        # Get rel vals from SUBINT header
        dt = subint['TBIN']
        spectra_per_subint = subint['NSBLK']
        bits_per_sample = subint['NBITS']
        num_subint[ii] = subint['NAXIS2']
        start_subint[ii] = subint['NSUBOFFS']
        time_per_subint = dt * spectra_per_subint

        # Go to the columns
        subint_hdu = hdus['SUBINT']
        # The following is a hack to read in only the first row 
        # from the fits file
        subint_hdu.columns._shape = 1
        
        # Identify the OFFS_SUB column number
        if 'OFFS_SUB' not in subint_hdu.columns.names:
            print "Can't find the 'OFFS_SUB' column!"
            sys.exit(0)
        else:
            colnum = subint_hdu.columns.names.index('OFFS_SUB')
            if ii==0:
                offs_sub_col = colnum 
            elif offs_sub_col != colnum:
                print "'OFFS_SUB' column changes between files 0 and %d!" % ii
                sys.exit(0)

            # Read the OFFS_SUB column value for the 1st row
            offs_sub = subint_hdu.data[0]['OFFS_SUB']
            numrows = int((offs_sub - 0.5 * time_per_subint) / \
                              time_per_subint + 1e-7)
            # Check to see if any rows have been deleted or are missing
            if numrows > start_subint[ii]:
                print "Warning: NSUBOFFS reports %d previous rows\n" \
                    "         but OFFS_SUB implies %s. Using OFFS_SUB.\n" \
                    "         Will likely be able to correct for this.\n" % \
                    (start_subint[ii], numrows)
            start_subint[ii] = numrows

        # This is the MJD offset based on the starting subint number
        MJDf =(time_per_subint * start_subint[ii])/psr_utils.SECPERDAY
        # The start_MJD values should always be correct
        start_MJD[ii] += MJDf
        MJDf = start_MJD[ii] - start_MJD[0]
        if MJDf < 0.0:
            print "File %d seems to be from before file 0!" % ii
            sys.exit(0)
        
        start_spec[ii] = (MJDf * psr_utils.SECPERDAY / dt + 0.5)

        # Comute the samples per file and the amount of padding
        # that the _previous_ file has
        num_pad[ii] = 0
        num_spec[ii] = spectra_per_subint * num_subint[ii]
        if ii>0:
            if start_spec[ii] > n_samp: # Need padding
                num_pad[ii-1] = start_spec[ii] - n_samp
                n_samp += num_pad[ii-1]
        n_samp += num_spec[ii]

        # Close the hdus
        hdus.close()
        n_samp = int(n_samp)
    return n_samp


def fb_samp(flist):
    """
    Count the number of samples in a SIGPROC filterbank file.
    
    Currently only handles one file, but would not be too hard
    to update for multifile.
    """
    fillist = flist
    
    if len(fillist) > 1:
        print "Currently can handle only one .fil file"
        sys.exit(0)
    
    fil_filenm = fillist[0]
    filhdr, hdrlen = sigproc.read_header(fil_filenm)
    n_samp = sigproc.samples_per_file(fil_filenm, filhdr, hdrlen)
    
    return n_samp
        

def get_samples(flist, dat_format):
    """
    Get the number of time samples from psrfits or 
    SIGPROC filterbank data formats.

    This is important so we know how many samples
    we want to output in our processing.

    Arguments are the file list and the 
    data format.  Currently accepted data formats
    are: 
        - psrfits
        - filterbank
    
    More coming (if necessary).
    """
    # Put dat_format in lowercase, just to be safe
    dat_format = dat_format.lower()
    
    # PSRFITS
    if (dat_format == 'psrfits'):
        n_samp = psrfits_samp(flist)
        
    # SIGPROC Filterbank
    elif (dat_format == 'filterbank'):
        n_samp = fb_samp(flist)

    # The rest are (currently) out of luck...
    else:
        print "Data type %s currently unsupported\n" %dat_type
        sys.exit(0)
        
    return n_samp
