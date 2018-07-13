# Written by Laura Spitler
#!/bin/env python

import numpy, sys
import numpy.random as random
from numpy.fft import fftn, ifftn

#from scipy.signal import fftconvolve

def make_noisyamp(mean, sigma, arrsize):

	data=random.normal(mean, sigma, arrsize)

	return data

def make_noisyspec(bias, sigma, arrsize):

	sqrt2=numpy.sqrt(2)
	if bias != 0: bias=bias-1/sqrt2

	nd=random.normal(0, 1, arrsize)
	pd=numpy.power(nd, 2)*sigma/sqrt2 + bias

	return pd

def calc_chandelays(dm, freq_lo, bw, nchan, tsamp, dtype='int'):	
	''' Calculate the channel delays for dedispersion
	Reference frequency is highest channel

	Parameters:
	dm = dispersion measure
	freq_lo = lowest frequency channel
	bw = bandwidth
	nchan = number frequency channels
	tsamp = sample time of spectra
	dtype = data type of the return array (default 'int')

	Returns:
	1D numpy array containing delay for each channel
	'''

	#Delay due to interstellar dispersion in milliseconds
	tdelay = lambda nu: 4.15e6*dm*(numpy.power(nu, -2) - numpy.power(nu[-1], -2))	

	#Define array of frequency channels
	freq=numpy.linspace(freq_lo, freq_lo+bw, nchan)

	#Calculate the appropriate channel delays
	tdel=tdelay(freq)

	if dtype=='int':
#		cdel=numpy.floor(tdel/tsamp)
		cdel=numpy.round(tdel/tsamp)
		cdel=numpy.cast['int'](cdel)
	else:
		cdel=tdel/tsamp

	return cdel

def gauss_weights(width, normalize='True'):
	# width = number of channels for FWHM
	# normalize: 'True'=normalize to unit area
	#	     'Power'=normalize to unit power
	#	     'False'=no normalization

	c=2*numpy.sqrt(numpy.log(2)*2)

	fg = lambda x, m, s, c: numpy.exp(-(x-m)**2/(2*(s/c)**2))

	x=numpy.arange(-2.0*width, width*2.0+0.1, 1.0)

	gw=fg(x, 0, width, c)

	if normalize=='True':
		gw=gw/numpy.sum(gw)
	elif normalize=='Power':
		gw=gw/(numpy.sqrt(numpy.sum(gw**2)))

	return gw

def gauss_weights2D(wx, wy):
	#Two dimensional gaussian weights

	fg2D = lambda x, y, wx, wy: numpy.exp(-(x**2/(2*(wx/c)**2) + y**2/(2*(wy/c)**2)))

	c=2*numpy.sqrt(numpy.log(2)*2)

	x=numpy.arange(-1.0*wx, wx+1.0, 1.0)
	y=numpy.arange(-1.0*wy, wy+1.0, 1.0)

	gw=numpy.array([])
	gw.shape=(2*wx+1,0)

	for i in range(len(y)):
		tmp=fg2D(x,y[i],wx,wy)
		tmp.shape=(2*wx+1,1)
		gw=numpy.concatenate((gw,tmp), axis=1)

	return gw

def exp_weights(width, normalize='True'):
#	a=lambda w: -w/numpy.log(0.01)
#	x=numpy.arange(width+1)
#	ew=numpy.exp(-x/a(width))
	x=numpy.arange(3*width)
	ew=numpy.exp(-x/float(width))

	if normalize=='True': ew/=numpy.sum(ew[:-1])

	return ew

def pulsar_template(cdel, width=1, mode='True', numhi=0):

	#Generate pulse template
	#'numhi' flag sets number of pulse chan to keep (i.e. filling factor)
	#'mode' flag: 'box' = define box profile
	#   otherwise 'mode' sets 'normalize' flag of gauss_weights func

	#Get number of channels
	nchan=len(cdel)
	if numhi == 0: numhi=nchan

	#Calculate pulse profile
	if mode == 'box':
		plen=max(cdel)+width
		gw=numpy.ones(width)
	elif mode == 'exp':
		gw=exp_weights(width)
		plen=max(cdel)+len(gw)
	else:
		gw=gauss_weights(width, normalize=mode)
		plen=max(cdel)+len(gw)

	#Create array of indecies with correct dispersion
	# for the columns of the template
	inarr=numpy.ones((numhi, len(gw)))
	t=numpy.arange(len(gw))
	cdel.shape=(nchan,1)
	inarr=inarr*t+cdel
	inarr=numpy.cast['int'](inarr)

	#Define array for channels (rows) of template
	c=numpy.arange(numhi)
	c.shape=(numhi,1)

	#Create empty template
	pul_temp=numpy.zeros((nchan, plen))

	#Add pulse
	pul_temp[c,inarr]=gw

	return pul_temp	

def add_pulsar(data, pulse_temp, tsamp, snr, period, mode='flat',ts=-1,dm=-1,verbose=False):
	#Period in seconds
	#tsamp in milliseconds

	#Define constants
	nchan,ntsamp=data.shape
	pullen=pulse_temp.shape[1]
	width=(len(numpy.where(pulse_temp[0,:] > 0)[0])-1)/4.0
	samp_per=period*1000.0/tsamp

	#Scale template by desired amplitude
	if mode=='flat':
		pulse_temp=snr*pulse_temp

	#Determine initial time sample
	if ts==-1:	
		samp_pul1=random.randint(0, pullen)
	else:
		samp_pul1=ts

	#Find array of starting samples for each pulse
	# based on period and max len of data
	spul=numpy.arange(samp_pul1, ntsamp-pullen-width, samp_per)

	#Add pulses
	for s in spul:
		data[:,s-2*width:s-2*width+pullen]=data[:,s-width:s-width+pullen]+pulse_temp

	#Report 
	if verbose==True:
		sys.stderr.write('New pulsar added\n')
		sys.stderr.write('snr: %3.2f dm: %d width: %1.1f period: %1.2f samp/per: %5.1f\n' % (snr,dm, width, period, samp_per))
		sys.stderr.write('Samples with a pulsar pulse: %s\n\n' % str(spul))

	return data

def add_singlepulse(data, pulse_temp, snr, ts=0, dm=-1, mode='flat', verbose=False):
	# data = 2D array of nchan x ntsamp
	# pulse_temp = pulse template
	# snr = signal to noise ratio of pulse

	#Find length of template and width of pulse
	pullen=pulse_temp.shape[1]
	width=(len(numpy.where(pulse_temp[0,:] > 0)[0])-1)/4.0

	if ts+pullen > data.shape[1]:	ts=0

	#Scale template to desired amplitude
	if mode=='flat': pulse_temp=snr*pulse_temp

	#Add single pulse
	data[:,ts-2*width:ts-2*width+pullen]+=pulse_temp

	#Report
	if verbose==True:
		sys.stderr.write('New single pulse added\n')
		sys.stderr.write('snr: %3.2f dm: %d loc: %d width: %1.1f\n\n' % (snr, dm, ts, width))

	return data

def add_spike(data, fw, tw, fchan, ts, amp=-1, verbose=False):
	# Add Gaussian spike to data
	# data = 2D array of nchan x ntsamp
	# fw, tw = width of spike in samples
	# fchan, ts = freq, time sample where spike center located
	# amp = amplitude of pulse, default exponential

	#Define gaussian weights
	gw=gauss_weights2D(fw, tw)

	#Get a random amplitude if requested
	if amp==-1:
		amp=random.exponential(1)

	#Add pulse
	data[fchan-fw:fchan+fw+1,ts-tw:ts+tw+1]=data[fchan-fw:fchan+fw+1,ts-tw:ts+tw+1] + amp*gw

	#Report
	if verbose=='True':
		sys.stderr.write('New spike added\n')
		sys.stderr.write('fchan: %d ts: %d fw: %d tw: %d amp %f\n\n' % (fchan, ts, fw, tw, amp))

	return data

def gen_inarr(nchan, ls, delays):
#	OLD METHOD
#	inarr=numpy.ones((nchan, ls))
#	t=numpy.arange(ls)
#	inarr=inarr*t+delays
#	inarr=numpy.cast['int'](inarr)
#	ANOTHER TRY-> SLOW
#	inarr=numpy.mgrid[0:nchan,0:ls][1]+delays

	inarr=numpy.arange(ls)
	inarr.shape=(1,ls)
	inarr=numpy.repeat(inarr,nchan,axis=0)+delays

	return inarr

#def add_array(data, inarr):
#	c=numpy.arange(data.shape[0])
#	c.shape=(data.shape[0],1)
	
#	return data[c,inarr]

def dedisperse(data, delays):
	#Dedisperse an array
	# 'data': 2D array of data with nchan rows and ntsamp columns
	# 'delay': vector of channel delays

	#Get data properties and define variables
	nchan,ntsamp=data.shape
	pl=delays[0]
	ls=ntsamp-pl	#Last sample that fits a full pulse width
	delays.shape=(nchan,1)

	#Generate "dispersed" indecies
	inarr=gen_inarr(nchan, ls, delays)

	#Define channel vector
	c=numpy.arange(nchan)
	c.shape=(nchan,1)

	#Address 2D data with desipered indecies upon returning
	return data[c, inarr]

def calc_timeseries(data, mode='sum'):
	#Calc timeseries (collapse freq dimension)
	# 'data': 2D array with dimensions nchan x ntsamp
	# 'mode': calculate timeseries using 'mean' or 'sum'

	if mode=='mean':	
		ts=numpy.mean(data, axis=0)
	else:
		ts=numpy.sum(data, axis=0)

	return ts

def calc_i2(data, mode='sum'):
	#Calc timeseries squared (collapse freq dimension)
	# 'data': 2D array with dimensions nchan x ntsamp
	# 'mode': calculate timeseries using 'mean' or 'sum'

	d2=numpy.power(data, 2)

	if mode=='sum':
		i2=numpy.sum(d2, axis=0)
	else:
		i2=numpy.mean(d2, axis=0)
		
	return i2

def threshold(ts, thr,  verbose=False):
	#Thresholds data with sigma clipping
	#  The time series is cleaned until the ratio of subsequent
	#  cleanings is less than 1%
	#ts = time series
	#thr = multiplier of std dev for thresholding
	#verbose = report mean, std deviation, ratio for each inter

	#Make local copy of ts to clean	
	tstmp=numpy.copy(ts)

	#Calculate statistics of uncleaned data
	sigold=numpy.std(tstmp)
	mold=numpy.mean(tstmp)


	#Do first clean stage
	inds=numpy.where(tstmp-mold > thr*sigold)[0]
	tstmp[inds]=mold
	sig=numpy.std(tstmp)
	m=numpy.mean(tstmp)

	if verbose == True: print mold, sigold
	if verbose == True: print len(inds)
	if verbose == True: print m, sig, sigold/sig-1.0

	#Loop through cleaning stages until ratio of 
	#  current stddev is less than 1 % the previous
	while sigold/sig - 1.0 > 0.01:

		inds=numpy.where(tstmp-m > thr*sig)[0]
		tstmp[inds]=m

		sigold=sig
		sig=numpy.std(tstmp)
		mold=m
		m=numpy.mean(tstmp)

		if verbose==True: print m, sig, sigold/sig-1.0

	#Now threshold with 'clean' statistics
	m,sig=mold,sigold
	inds=numpy.where(ts-m > thr*sig)[0]

	return inds,sig,m

def calc_modindex(i1, i2):
	#Calculate modulation index
	#  'i1','i2' = numbers or 1D arrays of intensity 
	# and intensity squared data

	mi=numpy.sqrt(i2 - i1**2)/i1

	return mi

def calc_stddev(i1, i2):
	#Calculate std deviation by hand
	std=numpy.sqrt(numpy.mean(i2) - numpy.mean(i1)**2)

	return std

def bad_chan(data, ch=-1, a=-1, width=1, verbose=False):
	#data = 2D array with nchan x ntsamp values
	#ch = ch to add RFI. Random if -1.
	#a = amp of RFI. Random if -1.

	nchan=data.shape[0]
	maxpwr=20

	#Calculate gaussian weights
	gw=gauss_weights(width, normalize='False')
	gw.shape=(len(gw),1)

	#Get chan and amp if requested random
	if ch==-1:
		ch=random.randint(0,nchan)
	if a==-1:
		a=random.randint(1, maxpwr)

	#Add bad channel to data
	data[ch-2*width:ch+2*width+1,:]=data[ch-2*width:ch+2*width+1,:]+a*gw

	#Report
	if verbose==True:
		sys.stderr.write('Added bad chan\n')
		sys.stderr.write('amp: %2.3f chan: %d\n\n' % (a,ch))

	return data

def bad_spec(data, t=-1, a=-1, width=1, verbose=False):
	#data = 2D array with nchan x ntsamp values
	#t = time sample to add RFI. Random if -1.
	#a = amp of RFI. Random if -1.

	ntsamp=data.shape[1]
	maxpwr=20

	#Define gaussian weights
	gw=gauss_weights(width, normalize='False')

	#Get time and amp if requested random
	if t==-1:
		t=random.randint(0,ntsamp)
	if a==-1:
		a=random.randint(1,maxpwr)

	#Add bad time sample
	data[:,t-2*width:t+2*width+1]=data[:,t-2*width:t+2*width+1]+a*gw

	#Report
	if verbose==True:
		sys.stderr.write('Added bad spec\n')
		sys.stderr.write('amp: %d tsamp: %d\n\n' % (a, t))

	return data

def gen_randdm(ndm, maxdm=1000):
	#Generate an array of random DMs

	dm=numpy.zeros(ndm)

	for i in range(ndm):
		dm[i]=random.randint(0,maxdm)

	return dm

def gen_randpwr(ndm, maxpwr=100):
	#Generate an array of random amps

	amp=numpy.zeros(ndm)

	for i in range(ndm):
		amp[i]=random.randint(1,maxpwr)

	return amp

def gen_poissonevents(rate, maxdur):
	#Generates a vector of poisson distributed events
	#Runs really slowly for large vectors
	# 'rate' - average rate of events
	# 'maxdur' - stop when events reach maxdur

	l=rate

	events=numpy.array([random.poisson(l)])
	e2=events
	sumdur=0

	while sumdur < maxdur:

		newevent=numpy.array([random.poisson(l)])
		events=numpy.concatenate((events, newevent+events[-1]))
		e2=numpy.concatenate((e2, newevent))
		sumdur=numpy.max(events)

	return events[0:-1],e2

def add_poissonevents3(data, rate, amp=1):
	#A somewhat contrived method for generating 2D poisson events
	#  with exponential amplitues: Runs quickly though
	#'data' = 2D array to add events to
	#'rate' = average seperation between events
	#'amp' = scale of expontial amplitudes

	nchan,ntsamp=data.shape

	#Generate array of samples for the Poisson events
	pe=random.poisson(rate, (nchan, ntsamp/rate))

	for i in range(pe.shape[0]-1,0,-1):
		pe[i]=numpy.sum(pe[0:i+1], axis=0)

	edge=pe[nchan-1]
	e2sum=numpy.zeros((pe.shape[1],))

	for i in range(edge.shape[0]):
		e2sum[i]=numpy.sum(edge[0:i+1])

	pe[:,1:]=pe[:,1:]+e2sum[:-1]
	pe=pe.transpose()
	pe=numpy.reshape(pe, (nchan*ntsamp/rate,))
	cut=numpy.where(pe < nchan*ntsamp)[0]
	pe=pe[cut]

	#Now generate amplitudes for events
	a=random.exponential(amp, nchan*ntsamp)
	d=numpy.zeros(nchan*ntsamp)
	d[pe]=a

	#Make event array the correct shape and add to data
	d.shape=(ntsamp,nchan)
	d=d.transpose()
	data=data+d
	
	return data

def smooth_ts(ts, nsm, mode='mean'):
	# Smooths time series by averaging (or summing) nsm samples
	# ts = 1D time series
	# nsm = number of samples summed is 2**nsm
	# mode = smooth by averaging or summing

	#Set variables
	nsamp=ts.shape[0]
	tstmp=numpy.copy(ts)
	nsm=2**nsm	#Now nsm= num samples not 2**nsm

	#If length of time series not an integer multiple
	# of smoothing factor, discard end samples	
	if nsamp % nsm != 0:
		s2c=nsamp%nsm
		tstmp=tstmp[0:nsamp-s2c]

	#Change shape
	tstmp.shape=(nsamp/nsm, nsm)

	#Smooth
	if mode=='mean':
		tstmp=numpy.mean(tstmp, axis=1)
	else:
		tstmp=numpy.sum(tstmp, axis=1)

	return tstmp

def boxcar_smooth(data, nsm, mode='mean'):
	'''Applies boxcar smoothing to a 2D array of data

	Parameters:
	data = 2D array - nchan x ntsamp
	nsm = log_2 of boxcar width (must be integer power of 2)

	Returns:
	sm_data - 2D array of smoothed data of form nchan x ntsamp
	'''
	datatmp=numpy.copy(data)
	nchan=datatmp.shape[0]
	ntsamp=datatmp.shape[1]
	nsm=2**nsm

	s2c=ntsamp%nsm

	if s2c != 0:
		sm_data=datatmp[:,0:-1*s2c]
	else:
		sm_data=datatmp

	sm_data.shape=(nchan, ntsamp/nsm, nsm)
	sm_data=numpy.mean(sm_data, axis=2)

	return sm_data

def rsmooth2(ts, mode='mean'):
	#Pascal smoothing function - smooths each sample with the next one
	# ts = 1D time series
	# mode = smooth by averaging or summing

	tslen=ts.shape[0]

	#If timeseries has an odd length, drop last sample
	if tslen%2==1:
		i0,i1=-2,-3
	else:
		i0,i1=-1,-2

	#Smooth
	if mode=='mean':
		sts=numpy.mean((ts[0:i1],ts[1:i0]), axis=0)
	else:
		sts=numpy.sum((ts[0:i1],ts[1:i0]), axis=0)

	return sts

def decimate(ts):
	#Decimate data by keeping ever other sample
	# ts = 1D array

	#Get length of time series
	tslen=ts.shape[0]

	#Define array of even samples
	inds=numpy.arange(0, tslen, 2)

	#Pull out even samples
	dts=ts[inds]

	return dts

def cluster(ts, overthr, nbin=2, mode='mean'):
        #Implementation of cluster or friends-of-friends algorithm
        # ts = times series 
        # overthr = sample in ts and ts2 that are over threshold

        #Make local copies
        tstmp=numpy.copy(ts)

        #Define clusters
        #Calculate index where each cluster ends
        cl_end=numpy.where(overthr[1:]-overthr[:-1] > nbin)[0]
        #Append last index to include trailing events
        cl_end=numpy.append(cl_end, len(overthr)-1)

        p=0
        params=numpy.zeros((len(cl_end),7))

        #Loop through clusters and calculate statistics 
        for i in range(len(cl_end)):
                #Define cluster for this loop
                ot=overthr[p:cl_end[i]+1]
                clust=ts[ot]

                ttmp=0
                for k in range(len(clust)):
                        ttmp=ttmp+k*clust[k]
                nsamp=len(clust)
                if mode=='sum': suma=numpy.sum(clust)
                else: suma=numpy.mean(clust)
                smax=overthr[p]+clust.argmax()
                amax=numpy.max(clust)
#               wgp=numpy.sum(clust)/amax       #sum/max
                wgp=ot[-1]-ot[0]+1
                tsum=ttmp/numpy.sum(clust)+overthr[p]
                tctr=overthr[p]+wgp/2
                if wgp%2 == 0: tctr-=0.5     #Add half-bin offset if width event

                params[i]=nsamp,smax,amax,tsum,suma,wgp,tctr
                p=cl_end[i]+1

        return params.transpose()

def cluster2D(data, overthr):
	# data = 2D freq-time dedispersed data
	# overthr = list of indecies for samples over threshold
	# Returns smoothed intensity (col 0), smoothed intensity squared (col 1)
	# and average sample number of pulse (col 2)

	#Define clusters
	#Calculate index where each cluster ends
	cl_end=numpy.where(overthr[1:]-overthr[:-1] > 2)[0]
	#Append last index to include trailing events
	cl_end=numpy.append(cl_end, len(overthr)-1)
	p=0
	params=numpy.zeros((len(cl_end),7))
	for i in range(len(cl_end)):

		#Define indexes for this cluster
		ot=overthr[p:cl_end[i]+1]   
		params[i,6]=len(ot)

		#Calculate mean parameters of the cluster
		smdtmp=numpy.mean(data[:,ot], axis=1)
		params[i,0]=numpy.mean(smdtmp)
		params[i,1]=numpy.mean(smdtmp**2)
		params[i,2]=numpy.mean(ot)

		#Calculate max parameters of the cluster
		smdtmp=numpy.mean(data[:,ot], axis=0)
		amax=smdtmp.argmax()
		params[i,3]=smdtmp[amax]
		params[i,4]=numpy.mean(data[:,ot[amax]]**2, axis=0)
		params[i,5]=ot[amax]

		p=cl_end[i]+1

	return params.transpose()

def fftconvolve(in1, in2, mode="full"):
    """Convolve two N-dimensional arrays using FFT. See convolve.
       NOTE: This function copied out of scipy.signal/signaltools.py
        so I didn't have to install scipy on more machines
    """
    s1 = numpy.array(in1.shape)
    s2 = numpy.array(in2.shape)
    complex_result = (numpy.issubdtype(in1.dtype, numpy.complex) or
                      numpy.issubdtype(in2.dtype, numpy.complex))
    size = s1+s2-1

    # Always use 2**n-sized FFT
    fsize = int(2**numpy.ceil(numpy.log2(size)))
    fsize = numpy.array([fsize])
    IN1 = fftn(in1,fsize)
    IN1 *= fftn(in2,fsize)
    fslice = tuple([slice(0, int(sz)) for sz in size])
    ret = ifftn(IN1)[fslice].copy()
    del IN1
    if not complex_result:
        ret = ret.real
    if mode == "full":
        return ret
    elif mode == "same":
        if product(s1,axis=0) > product(s2,axis=0):
            osize = s1
        else:
            osize = s2
        return _centered(ret,osize)
    elif mode == "valid":
        return _centered(ret,abs(s2-s1)+1)

def mf_fftconv(ts, width, mode):
	#Matched filtering using convolution
	# ts = time series; 1D or 2D array
	# width = width of matched filter
	# mode = filter type: 'gauss' or 'boxcar'
	# If ts 2D, each row is convolved with the Gaussian template
	#   with no convolution in column dimension

	#Num dim in data
	dndim=ts.ndim

	#Define filter weights
	if mode == 'gauss':
		gw=gauss_weights(width, normalize='True')
	elif mode == 'exp':
		gw=exp_weights(width, normalize='True')
	elif mode == 'boxcar':
#		gw=numpy.zeros(2*width)
#		gw[int(width)/2:-1*int(width)/2]=1.0/width
		gw=numpy.ones(width)/width
	else:
		raise ValueError('Incorrect \'mode\' parameter given')

	#Create filter array
	lgw=len(gw)
	mf=numpy.zeros(2*lgw)
	mf[lgw/2:-1*lgw/2]=gw

	if dndim==1:
 		fc=fftconvolve(mf, ts)
		return fc[lgw-1:-1*lgw]
	else:
		smdata=numpy.zeros(ts.shape)

		for c in range(ts.shape[0]):
			fctmp=fftconvolve(mf, ts[c])
			smdata[c]=fctmp[lgw-1:-1*lgw]

		return smdata

def calc_chandiff(dm_hi, dm_lo, freq_lo, bw, nchan, tsamp):	
	# freq_lo, bw in MHz
	# tsamp in millisec
	# Function copied from calc_chandelays 
	# to more properly calculate differences between DMs

	#Delay due to interstellar dispersion in milliseconds
	tdelay = lambda dm, nu: 4.15e6*dm*(numpy.power(nu, -2) - numpy.power(nu[-1], -2))	

	#Define array of frequency channels
	freq=numpy.linspace(freq_lo, freq_lo+bw, nchan)

	#Calculate the appropriate channel delays
	tdel=tdelay(dm_hi, freq) - tdelay(dm_lo, freq)
	cdel=tdel
#	cdel=numpy.floor(tdel/tsamp)
	cdel=numpy.round(tdel/tsamp)
#	cdel=numpy.cast['int'](cdel)

	return cdel

def fold_ts(ts, period, tsamp):

    nsamp_per=int(period/tsamp+0.5)
    num_per=int(len(ts)/nsamp_per)
    max_samp=nsamp_per*num_per

    print "Number of samples per period: %d" % nsamp_per
    print "Number of full periods in the time series: %d" % num_per
    print "Maximum sample in time series: %d" %  max_samp

    ts2fold=ts[:max_samp]

    ts2fold.shape=(num_per, nsamp_per)
    print ts2fold.shape
    ts_folded=numpy.mean(ts2fold, axis=0)

    return ts_folded

