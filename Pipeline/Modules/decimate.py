''' Module to perform decimation and smoothing on a dynamic spectrum.
    Assumed raw data is in a numpy array, ready for processing.
'''

# General Imports
import numpy as np
import scipy.signal as sig
import matplotlib.pyplot as plt

def block_avg(data, tsamp, vsamp):
    ''' Compute a block average of the dynamic spectrum <data>. 
        Desired block sizes for time/frequency averaging must be set
        as the global variables tsamp/vsamp respectively.
    
        Parameters:
            data (2D numpy array) -- dynamic spectrum to average
            tsamp (int) -- number of time samples to block
            vsamp (int) -- number of frequency samples to block
    '''

    [vchan, tchan] = data.shape    
    nT = int(tchan / tsamp)
    nV = int(vchan / vsamp)
    print(nT, nV)
    out = np.zeros((nV,nT))    
    for t in range(nT):
        for v in range(nV):
            oldT = t * tsamp
            oldV = v * vsamp
            out[v,t] = np.mean(data[oldV:oldV+vsamp, oldT:oldT+tsamp])

    return out

def decimate(data, tsamp, vsamp):
    ''' Sample a dynamic spectrum, with sampling periods tsamp/vsamp in
        time and frequency respectively.
        Parameters:
            data (2d numpy array) -- dynamic spectrum
            tsamp (int) -- time axis sampling period (in bins)
            vsamp (int) -- frequency axis sampling period (in bins)
    '''
    vchan, tchan = data.shape
    nV = int(vchan / vsamp)
    nT = int(tchan / tsamp)

    new_data = np.zeros((nV,nT))
    for v in range(nV):
        for t in range(nT):
            new_data[v,t] = data[v*vsamp, t*tsamp]

    return new_data



def convolve_smooth_2d(data, fil):
    ''' Convolve, using FFTs and the Convolution Theorem, 
        a 2d array <data> with a smoothing kernel (impulse response) <fil>. 
        The output array is larger than the input. In each dimension, the output's 
        size is equal to the sum of inputs' size minus one. 
        (i.e. If <data> has 50 time bins, and <fil> has 3 time bins, the output
        will have 50+3-1 = 52 time bins.) 
        Parameters:
            data (2d numpy array) -- dynamic spectrum
            fil (2d numpy array) -- "smoothing kernel" (finite impulse response)
    
        Return:
            2d convolution of <data> with <fil>
    '''
    vchan, tchan = data.shape
    vfil, tfil = fil.shape
    
    # get fft/convolution dimensions
    V = vchan + vfil - 1
    T = tchan + tfil - 1
    
    # zero pad input arrays
    fil = np.concatenate((fil, np.zeros((vfil, T-tfil))), axis=1)
    data = np.concatenate((data, np.zeros((vchan, T-tchan))), axis=1) 
    fil = np.concatenate((fil, np.zeros((V-vfil, T))), axis=0)
    data = np.concatenate((data, np.zeros((V-vchan, T))), axis=0) 

    # compute ffts
    data_fft = np.zeros((V, T),dtype=complex)
    fil_fft = np.zeros((V, T),dtype=complex)
    for v in range(V):
        data_fft[v,:] = np.fft.fft(data[v,:])
        fil_fft[v,:] = np.fft.fft(fil[v,:])
    for t in range(T):
        data_fft[:,t] = np.fft.fft(data_fft[:,t])
        fil_fft[:,t] = np.fft.fft(fil_fft[:,t])
    
    '''
    # built-in 2d ffts
    data_2dfft = np.fft.fft2(data)
    fil_2dfft = np.fft.fft2(fil)
    print(data_fft - data_2dfft)
    print(fil_fft - fil_2dfft)
    '''
    # use convolution theorem
    prod = np.multiply(data_fft, fil_fft)
    conv = np.fft.ifft2(prod)
    conv = conv.astype(float) # convert complex entries to real entries
    
    # Note: conv has dimensions:  (vchan + vfil - 1) x (tchan + tfil - 1)
    print(conv.shape)
    return conv



# Functions that generate various smoothing elements:
    
def gaussian(width, sigma, axis='t'):
    ''' Return a 1d Gaussian with stddev <sigma>, and total width <width>,
        normalized to have area 1.
        The parameters should be given in the units of the correct axis 
        (time/frequency). e.g. seconds/MHz respectively
        
        Parameters:
            width -- total width of Gaussian array
            sigma -- standard deviation
            axis -- time or frequency. Essentially determined unit conversion    
    '''

    if axis == 't':
        g = (sig.gaussian(width, sigma) / (np.sqrt(2*np.pi) * sigma))
        return np.reshape(g, (1,width))

    elif axis == 'v':
        g = (sig.gaussian(width, sigma) / (np.sqrt(2*np.pi) * sigma))
        return np.reshape(g, (width,1))
    
    else:
        print("Axis parameter is invalid. Valid options are 't' and 'v'.")
        return None
    

def gaussian_2d(T_width, V_width, T_sigma, V_sigma):

    # Get individual gaussians
    T_gaussian = gaussian(T_width, T_sigma, 't')
    V_gaussian = gaussian(V_width, V_sigma, 'v')

    # Make 2d Gaussian
    return np.outer(V_gaussian, T_gaussian)
    # NOTE: maybe not optimized for symmetric inputs?
    

def block(width, axis='t'):
    ''' Return a simple block to be used for smoothing. '''

    if axis == 't':
        return (np.ones((1,width)) / width)
    elif axis == 'v':
        return (np.ones((width,1)) / width)
    else:
        print("Axis parameter is invalid. Valid options are 't' and 'v'.")
        return None


def block_2d(T_width, V_width):
    return np.ones((V_width, T_width)) / (T_width * V_width)


def custom():
    ''' The user can define a custom smoothing kernel. The kernel will be
        convolved (2-dimensional) with the raw data.
    
        Return: smoothing kernel as a 2d numpy array
    '''

    return



def call_filter(sd, data):

    ''' Create the desired smoothing kernel, and convolve it with 
        the raw data. Return the smoothed data. 
        Parameters:
            sd (dictionary)-- (passed from `decimate_method.py`) contains
                  smoothing parameters
            data (2D numpy array) -- raw data
    '''

    kernel_list = sd['kernels']
    T_width = sd['T_width']
    V_width = sd['V_width']
    T_sigma = sd['T_sigma']
    V_sigma = sd['V_sigma']

    if T_width == 0:
        raise ValueError("Smoothing kernel has zero width in time dimension. Cannot "\
                          "convolve data with zero-dimension kernel. Exiting...")
    if V_width == 0:
        raise ValueError("Smoothing kernel has zero width in frequency dimension. Cannot "\
                          "convolve data with zero-dimension kernel. Exiting...")

    for n in range(len(kernel_list)):
        current = kernel_list[n].split()[0]
        if current == 'gaussian2d':
            kernel = gaussian_2d(T_width, V_width, T_sigma, V_sigma)
        elif current == 'gaussianT':
            kernel = gaussian(T_width, T_sigma, 't') 
        elif current == 'gaussianV':
            kernel = gaussian(V_width, V_sigma, 'v')
        elif current == 'block2d':
            kernel = block_2d(T_width, V_width)
        elif current == 'blockT':
            kernel = block(T_width, 't')
        elif current == 'blockV':
            kernel = block(V_width, 'v')
        elif current == 'custom':
            kernel = custom()
        else:
            kernel = None       
            print("kernel format is invalid")
        
        print("Convolving data with %s kernel" %(current))
        data = convolve_smooth_2d(data, kernel)
        
    return data
        


def decimate_and_smooth(gd, sd, data, do_avg=False, do_smooth=True, do_decimate=True):

    # sd -- global and smoothing parameters (dictionary)

    tsamp = gd['tsamp']
    vsamp = gd['vsamp']
   
    print(data.shape)
    
    #plt.imshow(data)
    plt.show()
    if do_avg == True:
        print("Block averaging raw data, with:\n\ttsamp=%d\n\tvsamp=%d" %(tsamp, vsamp)) 
        data = block_avg(data, tsamp, vsamp)
        #plt.imshow(data)
        plt.show()
    else:
        print("No averaging selected.")

    if do_smooth == True:
        print("Smoothing the block averaged data.\n\nConvolution Kernels: %s" %(str(sd['kernels'])))
        smooth_data = call_filter(sd, data) 
        #plt.imshow(smooth_data)
        plt.show()
    else:
        print("No smoothing selected.")
        smooth_data = data

    if do_decimate == True:
        print("Decimating smoothed data.\n Time sampling period (bins): %d\n "\
              "Frequency sampling period (bins): %d" %(tsamp, vsamp))
        dec_data = decimate(smooth_data, tsamp, vsamp)
        #plt.imshow(dec_data)
        plt.show()
    else:
        print("No decimation performed.")
        dec_data = smooth_data


    dec_data = dec_data[3:,:]
    return dec_data
