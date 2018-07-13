

# Friends of Friends search algorithm.
# Assume that we already have a raw, masked dynamic spectrum stored in a numpy array

# General Imports
import numpy as np
import matplotlib.pyplot as plt
import math
import scipy.odr as odr
from scipy.stats import linregress
import scipy.ndimage as ni
from subprocess import call

# Local Imports
import params

kDM = 4148.808 # MHz^2 / (pc cm^-3)

class Cluster:

    def __init__(self, coords, sigs, std):
        ''' <coords> is a tuple containing two arrays (should be
            output of np.where()), which contain respectively
            the frequency and time coordinates of samples in the cluster. <sigs>
            contains the values of the dyamic spectra at these coordinates. '''
        self.t_co = coords[1]               # time coordinates array
        self.v_co = coords[0]               # frequency coordinates array
        self.sigs = sigs                    # signal values array
        self.global_std = std
 
        self.N = np.size(sigs)              # number of samples in blob
        self.t_mean = np.mean(self.t_co)    # mean of time coords of samples in blob
        self.t_range = (np.min(self.t_co),np.max(self.t_co))   # time range of blob in bins (tuple)
        self.v_mean = np.mean(self.v_co)    # mean of freq. coords of samples in blob
        self.v_range = (np.min(self.v_co),np.max(self.v_co))   # frequency range of blob in bins (tuple)
        self.sig_mean = np.mean(sigs)       # signal mean
        self.sig_max = np.max(sigs)         # maximum signal value
        self.SNR_mean = self.sig_mean / self.global_std
        self.SNR_max = self.sig_max / self.global_std
        argmax = np.argmax(sigs)
        self.coord_max = (self.v_co[argmax],self.t_co[argmax]) # coordinates of sample with max signal value
        
        self.clust_SNR = ((self.sig_mean * math.sqrt(self.N)) / self.global_std) 

    def lin_fit(self,C):
        ''' Perform orthogonal linear regression on this Cluster.
            The slope and intercept are stored as a tuple in the field <linear>'''
        
        linear_fit = odr.Model(lin_func)
        data = odr.Data(C * self.t_co,self.v_co) # y-axis is frequency
        odr_inst = odr.ODR(data, linear_fit, beta0=[0.0,self.v_mean])
        output = odr_inst.run()
        (slope,intercept) = output.beta[0],output.beta[1]
        self.linear = (C * slope,intercept)

    def DM_fit(self, tstart, v_max_index):
        ''' Perform orthogonal DM (inverse square) regression on this Cluster.
            The fitted DM value is stored in the field <DM>.'''
        # Note: frequency axis is flipped, because high freqs correspond to low array indices
        #print self.t_co
        #print self.v_co
        t_co = (self.t_co * params.avg_samp * params.dt) + tstart
        v_co = ((v_max_index-self.v_co) * params.avg_chan * params.dv) + params.freqs[0]
        #print t_co
        #print v_co
        #print DM_func([560.0*kDM], v_co, t_co[0], v_co[0])
        data = odr.Data(v_co,t_co) # y-axis is time
        DM_mod = odr.Model(DM_func, extra_args=(t_co[0],v_co[0]))
        odr_inst = odr.ODR(data, DM_mod, beta0=[560.0*kDM])
        output = odr_inst.run()
        self.DM = output.beta[0] / kDM
        
        #print "DM = " + str(self.DM)
        #plt.plot(DM_func([self.DM],v_co,t_co[0],v_co[0]),v_co)
        #plt.show()
        #plt.scatter(t_co,v_co)
        #plt.show()

    def add(self, coord, sig):
        # coord is tuple, sig is the signal at that coordinate
        self.v_co = np.append(self.v_co,coord[0])
        self.t_co = np.append(self.t_co,coord[1])
        self.sigs = np.append(self.sigs,sig)
         
        self.N += 1
        self.t_mean = (self.t_mean * (self.N-1) + coord[1]) / self.N
        self.v_mean = (self.v_mean * (self.N-1) + coord[0]) / self.N
        if coord[0] > self.v_range[1]:
            self.v_range = (self.v_range[0],coord[0])
        elif coord[0] < self.v_range[0]:
            self.v_range = (coord[0],self.v_range[1])
        if coord[1] > self.t_range[1]:
            self.t_range = (self.t_range[0],coord[1]) 
        elif coord[1] < self.t_range[0]:
            self.t_range = (coord[1],self.t_range[1])

        self.sig_mean = (self.sig_mean * (self.N-1) + sig) / self.N
        if sig > self.sig_max:
            self.sig_max = sig       
            self.coord_max = coord

        #if coord[0] > self.vmax:
        #    self.vmax = coord[0]
        #elif coord[0] < self.vmin:
        #    self.vmin = coord[0]
        #if coord[1] > self.tmax:
        #    self.tmax = coord[1]
        #elif coord[1] < self.tmin:
        #    self.tmin = coord[1]
        #self.vmax = max(self.vmax,coord[0])
        #self.vmin = min(self.vmin,coord[0])
        #self.tmax = max(self.tmax,coord[1])
        #self.tmin = min(self.tmin,coord[1])

    def statline(self):
        '''Returns a string of the class attributes separated by tabs.'''
        return "%d\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\n" \
               %(self.N, self.clust_SNR, self.sig_mean, self.sig_max, 
                 self.SNR_mean, self.SNR_max, self.t_range[0],
                 self.t_range[1], self.v_range[0], self.v_range[1], 
                 self.linear[0], self.DM)


def manhattan(x1,x2):
    '''Return the Manhattan distance between two coordinates 
       given by tuples x1 and x2'''
    dist = abs(x1[0]-x2[0]) + abs(x1[1]-x2[1])
    return dist


def avg_time(data, dt):
        
    ''' averages a dynamic spectrum in time (x axis) over every <dt> time samples'''
    (vchan,tchan) = data.shape
    t_num = int(tchan / dt)
    avg_data = np.zeros([vchan,t_num])
    for t in range(t_num):
        t_index = t * dt
        for v in range(vchan):
            avg_data[v,t] = np.mean(data[v,t_index:(t_index+dt)])
    return avg_data

def avg_freq(data, dv):
    ''' average a dynamic spectrum in frequency (y axis) over every <dv> frequency samples'''
    (vchan,tchan) = data.shape
    v_num = int(vchan / dv)
    avg_data = np.zeros([v_num,tchan])
    for v in range(v_num):
        v_index = v * dv
        for t in range(tchan):
            avg_data[v,t] = np.mean(data[v_index:(v_index+dv),t])
    return avg_data


def mean_rms(data):
    ''' Return the mean and RMS (in a tuple) of a data array.
        Note that the variance is computed as:
            var = (RMS)^2 - (mean)^2 
    '''
    (vchan,tchan) = data.shape
    ssum = 0.0
    dsum = 0.0
    for t in range(tchan):
        for v in range(vchan):
            ssum += (data[v,t])**2
            dsum += data[v,t]

    num_pixels = vchan * tchan
    mean_ssum = ssum / num_pixels
    rms = math.sqrt(mean_ssum)
    mean = dsum / num_pixels

    return (mean,rms)

def iterative_stats(data, out, thresh):
    ''' Return the mean and standard deviation (in a tuple) of a data array. 
        Iteratively remove outlying data points from the calculation. If a data point has   
        a value greater than (out * stddev), it is masked and removed from the next calculation.
        The convergence criteria is:
            (mean - mean_prev)  / mean  <  thresh
            (std - std_prev) / std  <  thresh
        i.e. once successive iterates of both mean and standard deviation are within 1% of each other, 
        the method terminates, and the latest evaluations of mean and stddev are returned.
    
    Arguments: (1) data -- a dynamic spectrum numpy array   
               (2) out -- data points that vary by more than (out * std_prev) are removed from the calculation
               (3) thresh -- successive iterations for mean and std must be within <thresh> for the method to terminate
    '''       
    (vchan,tchan) = data.shape
    size = data.size
    mask = np.zeros((vchan,tchan))
    #mask = {}
    #for v in range(vchan):
    #    for t in range(tchan):
    #        mask[(v,t)] = 1

    mean_prev = 0.0;
    std_prev = 0.0;

    mean = np.mean(data)
    std = np.std(data)
    
    #print "mean= " + str(mean)
    #print "rms= " + str(rms)
    #print "std= " + str(std)

    while (abs(mean_prev-mean) / mean) > thresh and (abs(std-std_prev) / std) > thresh:
        mean_prev = mean
        std_prev = std    
        ssum = 0.0 # squared sum
        rsum = 0.0 # regular sum
        for v in range(vchan):
            for t in range(tchan):
                if mask[v,t] == 0: # if not masked
                    if abs(data[v,t]-mean_prev) > (out * std_prev):
                        mask[v,t] = 1
                        size -= 1
                    else:
                        ssum += (data[v,t])**2
                        rsum += data[v,t]    
        mean = rsum / size
        rms_squared = ssum / size
        std = math.sqrt(rms_squared - mean**2)
        
        ree = np.ma.array(data,mask=mask)
        mean2 = ree.mean()
        std2 = ree.std()
        print "mean= " + str(mean)
        print "std= " + str(std)
        #print "size = " + str(size)

    #print mask
    return (mean,std)


def mask1(data, mean, std, thresh):
    ''' Create a binary mask for some dynamic spectrum. 
        Ones flag high signal pixels; all other pixels are
        represented as zeros.
        A high signal pixel is determined as follows:
            (pixel_value - mean) > (thresh * std)
    '''
    (vchan,tchan) = data.shape
    mask = np.zeros([vchan,tchan])
    thresh_val = std * thresh
    for v in range(vchan):
        for t in range(tchan):
            val = data[v,t]
            if val - mean  > thresh_val:
                mask[v,t] = 1

    return mask

def lin_func(beta, x):
    ''' simple linear funcion used for orthogonal regression'''
    return (beta[0] * x) + beta[1]

def DM_func(beta, v, *args):
    ''' Inverse square function used for DM regression'''
    t1 = args[0]
    v1 = args[1]
    return (beta[0] / v**2) + t1 - (beta[0] / v1**2)


# Parameters: (1) data -- raw dynamic spectrum   (2) m1 -- single pixel threshold, 
#               as a fraction of standard deviation   (3) m2 -- blob RMS threshold, as frac of single pixel RMS

def fof(data, m1, m2, tsamp, vsamp, t_gap, v_gap):
    ''' t_gap and v_gap must be even'''
    '''Arguments:
            (1) data -- raw dynamic spectrum array
            (2) m1 -- single pixel SNR threshold
            (3) m2 -- cluster SNR threshold
            (4) tsamp -- time
            (5) vsamp
            (6) t_gap -- number of empty time samples allowed...
            (7) v_gap -- number of empty freq. samples allowed... 
                 between pixels in the same cluster
    '''
    avg_t_data = avg_time(data,tsamp)
    avg_tv_data = avg_freq(avg_t_data,vsamp)

    (mean,std) = iterative_stats(avg_tv_data, 3, 0.01)
    #print "mean= " + str(mean)
    #print "std= " + str(std)
    mask = mask1(avg_tv_data, mean, std, m1)
    (vchan,tchan) = mask.shape
    C = float(vchan) / tchan # used in linear fitting
    # construct a structuring element:
    se = np.ones([v_gap+1,t_gap+1])
    # dilate the mask
    dil = ni.morphology.binary_dilation(mask, structure=se).astype(mask.dtype)
    # label contiguous clusters
    (labeled_dil, num_clusters) = ni.measurements.label(dil)
    # remove filler values from the clusters
    for v in range(vchan):
        for t in range(tchan):
            if mask[v,t] == 0:
                 labeled_dil[v,t] = 0

    #np.save("test.npy", mask)   
    #print mask
    #print se 
    #print dil
    #print labeled_dil
    #plt.imshow(avg_tv_data, cmap='gray_r')
    #plt.show()
    #plt.imshow(dil)
    #plt.show()

    clust_list = []
    filename = "clust_%.1f_%d_%d_%d_%d_%d" %(m1,m2,tsamp,vsamp,t_gap,v_gap)
    f = open(filename + ".txt", "w")
    f.write("fof results, with\nm1=%.2f   m2=%.2f   tsamp=%.2f   vsamp=%.2f   t_gap=%.2f   v_gap=%.2f\n\n" \
            %(m1,m2,tsamp,vsamp,t_gap,v_gap))
    f.write("N \tclust_SNR\t\tsig_mean\tsig_max\t\tSNR_mean\tSNR_max\t\tt_min\t\tt_max\t\t\tv_min\t\tv_max\t\tslope\tDM\n")

    # create cluster objects and add to <clust_list>
    # write cluster's stats to a text file
    for n in range(num_clusters):
        coords = np.where(labeled_dil==(n+1))
        sigs = avg_tv_data[coords]
        # check cluster SNR threshold
        new = Cluster(coords,sigs,std)
        clust_list.append(new)
        
        if new.clust_SNR > m2: # CLUSTER FILTER
            labeled_dil[coords] = (n+1) + num_clusters

            # Do linear fit and DM fit.
            new.lin_fit(C)
            new.DM_fit(128.00, vchan-1)
            #print new.linear
            #print new.DM
            ''''temp = np.zeros(labeled_dil.shape)
            temp[coords] = 1
            plt.imshow(temp)
            plt.show()'''

            f.write(new.statline())
            #print new.statline()
    f.close()
    call(["mv", filename + ".txt", "clusters_DM"])    
 
    plt.imshow(labeled_dil)
    #plt.show()
    plt.savefig(filename + ".png")
    call(["mv", filename + ".png", "clusters_DM"])     
    
    print "Finished Search."
