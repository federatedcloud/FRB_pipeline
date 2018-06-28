# =============================================================================
# Important directory locations
# =============================================================================
#fits_dir = "/mnt/data1/rsw_test/pipeline/psrfits"
fits_dir = "/mnt/data1/pete/data"

# Names of both .fits files to combine (if using combine_mocks)
combinefile1 = "4bit-p2030.20121102.G175.04-00.26.C.b4s0g0.00000"
combinefile2 = "4bit-p2030.20121102.G175.04-00.26.C.b4s1g0.00000"

# Base name of fits files in FITS dir
#basename = "waller"
basename = "testing_combine_mocks" #"waller_test_combined_0001"

# Search output directory
search_dir = "/mnt/data1/pete/test/combine_mocks/search"


# =============================================================================
# Processing steps to do
# =============================================================================
do_combine_mocks = 1    # Run combine_mocks on the upper and lower subbands
do_rfifind       = 1    # Run PRESTO rfifind and generate a mask
do_prepsub       = 1    # Run PRESTO prepsubband dedispersion
do_fft           = 0    # FFT *dat files before accelsearch
do_candsearch    = 0    # Run PRESTO accelsearch on the data
do_presto_sp     = 1    # Run PRESTO singlepulse.py
do_mod_index     = 1    # Run PALFA2 modulation index calculation
do_make_plots    = 1    # Plots and shows single pulse candidates
do_param_cp      = 0    # copy parameter file to output directory 


# =============================================================================
# Data Format Type
# Use PRESTO naming conventions (i.e. 'filterbank' or 'psrfits')
# =============================================================================
dat_type = 'psrfits'


# =============================================================================
# Important Script Locations
# =============================================================================
#singlepulse = 'single_pulse_search.py'
singlepulse = "/mnt/data1/pete/code/FRB_pipeline/spitler_pipeline/mod_sp.py"; sp_modified = True

palfa_mi = "/home/jovyan/modulation_index/mi_src/palfa_mi"


# =============================================================================
# PRESTO Command Parameters
# =============================================================================
# rfifind params
use_mask  = 1           # use the rfi mask?
rfi_time  = 5.0         # sec, time over which stats are calc'd in rfifind (d: 30)
time_sig  = 15          # The +/-sigma cutoff to reject time-domain chunks (d: 10)
freq_sig  = 6           # The +/-sigma cutoff to reject freq-domain chunks (d: 4)
chan_frac = 0.3         # The fraction of bad channels that will mask a full interval (d: 0.7)
int_frac  = 0.3         # The fraction of bad intervals that will mask a full channel (d: 0.3)
rfi_otherflags = '-noscales -nooffsets -noweights ' #

# Dedispersion parameters
# NOTE: Will do multi-pass sub-band dedispersion if and only if dmcalls > 1
dmlow = 500 
ddm   = 5
dmcalls    = 1
dmspercall = 20         # 250
nsub       = 960        # 608
dsubDM     = 0.0
downsample = 1
prep_otherflags = '-noscales -nooffsets -noweights ' # other flags for prepsubband

# accelsearch parameters
use_fft = 1             # Search FFTs (1) instead of dats (0)
zmax = 100              # Max acceleration in fourier bins
numharm = 16            # Number of harmonics to sum
freq_lo = 0.1           # Hz, lowest freq to consider real
freq_hi = 2000.0        # Hz, highest freq to consider real
zap_str = ''            # Put zap stuff here, if desired
accel_cores = 1         # number of processing cores

# Single pulse
max_width = 1.0         # Max pulse width (seconds)
dtrend    = 1           # Detrend factor 1-32 powers of two 
sp_otherflags = "-f "   # Other flags


# =============================================================================
# Maskdata and Modulation Index Calculation Parameters
# =============================================================================
md_flags = "-nobary -noweights -nooffsets -noscales -mask "
md_otherflags = " -o junk.dat "


# =============================================================================
# Plotting Parameters
# =============================================================================
do_plot_color = 1       # Plots color and shows single pulse candidates
do_plot_grey = 1        # Plots grey and shows single pulse candidates
do_plot_reverse = 1     # Plots reverse grey and shows single pulse candidates

fildir = search_dir
filfile = "%s/raw_data_with_mask.fits" %fildir

#freqs = 1214.28955078 + np.arange(nsub) * 0.336182022493
dt = 6.54761904761905E-05
tstart = 128.0          # sec
tread  = 0.5            # sec

avg_chan = 10
avg_samp = 20
dm0 = 557.0
vmin = 6
vmax = 7


# =============================================================================
# Sifting parameters (copied mostly from PRESTO's ACCEL_sift.py):
#--------------------------------------------------------------
min_num_DMs = 2         # Min number of DM bins a candidate must show up in to be "good"
low_DM_cutoff = 0.0     # Lowest DM to be considered a "real" pulsar

# The following show up in the sifting.py PRESTO module:

# Ignore candidates with a sigma (from incoherent power summation) less than this
sigma_threshold = 3.0   # was 3.0    
# Ignore candidates with a coherent power less than this
c_pow_threshold = 100.0
# If the birds file works well, the following shouldn't
# be needed at all...  If they are, add tuples with the bad
# values and their errors.
#        (ms, err)
known_birds_p = []
#        (Hz, err)
known_birds_f = []
# The following are all defined in the sifting module.
# But if we want to override them, uncomment and do it here.
# You shouldn't need to adjust them for most searches, though. 

# How close a candidate has to be to another candidate to
# consider it the same candidate (in Fourier bins)
r_err = 1.1
# Shortest period candidates to consider (s)
short_period = 1./freq_hi
# Longest period candidates to consider (s)
long_period = 1./freq_lo
# Ignore any candidates where at least one harmonic does exceed this power
harm_pow_cutoff = 8.0
#--------------------------------------------------------------
