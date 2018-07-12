import numpy as np
import matplotlib.pyplot as plt
import sys

kdm = 4148.808 # MHz^2 / (pc cm^-3)

def dm_delay(f1, f2, DM, kdm=kdm):
    return kdm * DM * (1.0 / (f1 * f1) - 1 / (f2 * f2))


def deltaT_old(ichan, dt, df, f0, kdm=kdm):
    return (kdm / dt) * ((f0 + ichan * df)**-2.0 - f0**-2)


def dmdt_old(DM, ichan, dt, df, f0, kdm=kdm):
    return int(np.round( DM * deltaT(ichan, dt, df, f0, kdm=kdm)))


def dmdt_float_old(DM, ichan, dt, df, f0, kdm=kdm):
    return DM * deltaT(ichan, dt, df, f0, kdm=kdm)


def deltaT(freqs, f0, dt, kdm=kdm):
    return (kdm / dt) * (freqs**-2.0 - f0**-2)


def dmdt(DM, freqs, f0, dt, kdm=kdm):
    return DM * deltaT(freqs, f0, dt, kdm=kdm)


def dedisperse_one(dspec, dm, dt, df, f0, kdm=kdm):
    nchans = dspec.shape[0]
    nt = dspec.shape[1]
    dsamps = np.array([ dmdt_old(dm, ichan, dt, df, f0, kdm=kdm) for ichan in xrange(nchans) ])
    dsamps -= np.min(dsamps)
    tpad = np.max(dsamps)
    outarr = np.zeros( nt + tpad )
    for ii in xrange(nchans):
        osl = slice(tpad - dsamps[ii], nt + tpad - dsamps[ii])
        outarr[osl] += dspec[ii]
    return outarr[tpad:nt + tpad] / float(nchans)


def dedisperse_dspec_old(dspec, dm, dt, df, f0, kdm=kdm):
    nchans = dspec.shape[0]
    nt = dspec.shape[1]
    dsamps = np.array([ dmdt_old(dm, ichan, dt, df, f0, kdm=kdm) for ichan in xrange(nchans) ])
    dsamps -= np.min(dsamps)
    tpad = np.max(dsamps)
    outarr = np.zeros( (nchans, nt + tpad) )
    for ii in xrange(nchans):
        osl = slice(tpad - dsamps[ii], nt + tpad - dsamps[ii])
        outarr[ii, osl] = dspec[ii]
    return outarr[:, tpad:nt + tpad]


def dedisperse_dspec(dspec, dm, freqs, f0, dt, kdm=kdm, reverse=False):
    nchans = dspec.shape[0]
    nt = dspec.shape[1]
    dsamps = dmdt(dm, freqs, f0, dt, kdm=kdm)
    #dsamps -= np.min(dsamps)
    if reverse:
        sgn = -1.0
    else:
        sgn = +1.0 
    
    dout = np.zeros( dspec.shape )
    for ii, dd in enumerate(dspec):
        ak = np.fft.rfft(dd)
        bfreq = np.arange(len(ak)) / (1.0 * len(dd))
        shift = np.exp(sgn * 1.0j * 2 * np.pi * bfreq * dsamps[ii])
        dd_shift = np.fft.irfft( ak * shift )
        dout[ii][:len(dd_shift)] = dd_shift[:]

    return dout


def dspec_avg_chan(dspec, freqs, avg_chan=1):
    Nchan = dspec.shape[1]
    n = int(Nchan / avg_chan)
    
    freq_out = np.zeros(n)
    dd_out = np.zeros( (dspec.shape[0], n) )

    for ii in xrange(n):
        sl = slice(ii * avg_chan, (ii+1) * avg_chan)
        freq_out[ii] = np.mean(freqs[sl])
        dd_out[:, ii] = np.mean(dspec[:,sl], axis=1)

    return freq_out, dd_out


def dspec_avg_time(dspec, avg_samp=1):
    Nsamp = dspec.shape[0]
    n = int(Nsamp / avg_samp)
    
    dd_out = np.zeros( (n, dspec.shape[0]) )

    for ii in xrange(n):
        sl = slice(ii * avg_samp, (ii+1) * avg_samp)
        dd_out[ii,:] = np.mean(dspec[sl, :], axis=0)

    return dd_out


def dspec_avg_chan_dm(dspec, freqs, f0, dt, avg_chan=1, dm0=0.0):
    dd_dm0 = dedisperse_dspec(dspec.T, dm0, freqs, f0, dt)
    avg_freqs, davg_dm0 = dspec_avg_chan(dd_dm0.T, freqs, avg_chan=avg_chan)
    davg = dedisperse_dspec(davg_dm0.T, dm0, avg_freqs, f0, dt, reverse=True)
    return avg_freqs, davg.T


def dspec_avg_time_dm(dspec, freqs, f0, dt, avg_samp=1, dm0=0.0):
    dd_dm0 = dedisperse_dspec(dspec.T, dm0, freqs, f0, dt)
    davg_dm0 = dspec_avg_time(dd_dm0.T, avg_samp=avg_samp)
    davg = dedisperse_dspec(davg_dm0.T, dm0, freqs, f0, avg_samp * dt, reverse=True)
    return davg.T


def dspec_avg_tf_dm(dspec, freqs, f0, dt, avg_chan=1, avg_samp=1, dm0=0.0):
    dd_dm0 = dedisperse_dspec(dspec.T, dm0, freqs, f0, dt)
    dd_dm0_t = dspec_avg_time(dd_dm0.T, avg_samp=avg_samp)
    avg_freqs, davg_dm0 = dspec_avg_chan(dd_dm0_t, freqs, avg_chan=avg_chan)
    davg = dedisperse_dspec(davg_dm0.T, dm0, avg_freqs, f0, avg_samp * dt, reverse=True)
    #return avg_freqs, davg.T
    return avg_freqs, davg


def dspec_avg_chan_dm_GHz(dspec, freqs, f0, dt, avg_chan=1, dm0=0.0):
    freqs_MHz = freqs * 1e3
    f0_MHz = f0 * 1e3

    dd_dm0 = dedisperse_dspec(dspec.T, dm0, freqs_MHz, f0_MHz, dt)
    avg_freqs_MHz, davg_dm0 = dspec_avg_chan(dd_dm0.T, freqs_MHz, avg_chan=avg_chan)
    davg = dedisperse_dspec(davg_dm0.T, dm0, avg_freqs_MHz, f0_MHz, dt, reverse=True)

    avg_freqs = avg_freqs_MHz / 1e3

    return avg_freqs, davg.T
