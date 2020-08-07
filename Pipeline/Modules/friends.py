
''' The module contains tools to run a Friends-of-Friends search algorithm.
    The main function is fof(), which is found at the bottom of this file.
    Most other functions defined in this module are called by fof(), 
    and some may also be useful for other purposes as well.
'''

# General Imports
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import math
import scipy.odr as odr
from scipy.stats import linregress
import scipy.ndimage as ni
from subprocess import call
from plotnpz import plot

# kDM -- Interstellar dispersion constant
kDM = 4148.808 # MHz^2 / (pc cm^-3)


class Cluster:
    
    ''' A class to store information about a cluster of pixels identified
        using the friends-of-friends algorithm.'''

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
        
        # Cluster SNR statistics. See Josh Burt's paper for math formula
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
        t_co = (self.t_co * tsamp * dt) + tstart
        v_co = ((v_max_index-self.v_co) * vsamp * dv) + vlow
        #print(DM_func([560.0*kDM], v_co, t_co[0], v_co[0]))
        data = odr.Data(v_co,t_co) # y-axis is time
        DM_mod = odr.Model(DM_func, extra_args=(t_co[0],v_co[0]))
        # Note: beta0 is initial estimate of DM*kDM
        odr_inst = odr.ODR(data, DM_mod, beta0=[560.0*kDM])
        output = odr_inst.run()
        self.DM = output.beta[0] / kDM


    def DM_extrapolate(self, vchan, tchan):

        # find the max time span for a single frequency band
        v_prev = 0
        t_seed = 0
        dT_max = 0
        for j in range(self.N):
            if self.v_co[j] == v_prev:
                dT_max = max((self.t_co[j] - t_seed), dT_max)
            else:
                t_seed = self.t_co[j]
            v_prev = self.v_co[j]

        #dT_width = int(dT_max / 2)

        mask = np.zeros((vchan,tchan))
        v_co = np.flip((np.arange(vchan) * vsamp * dv) + vlow,0)
        # dispersed times, computed assuming t0 = self.t_mean, ignore tstart
        t_mean = (self.t_mean * dt * tsamp)
        v_mean = vhigh - (self.v_mean * dv * vsamp)
        delayed_Ts = DM_func([self.DM * kDM], v_co, t_mean, v_mean)
        delayed_Tbins = (delayed_Ts / (dt * tsamp)).astype(int)

        t0 = int(self.t_mean)
        for v in range(vchan):
            T = delayed_Tbins[v]
            mask[v, (T - dT_max):(T + dT_max)] = 1

        self.DM_mask = mask


    def lin_extrapolate(self, vchan, tchan):

        # find the max time span for a single frequency band
        v_prev = 0
        t_seed = 0
        dT_max = 0
        for j in range(self.N):
            if self.v_co[j] == v_prev:
                dT_max = max((self.t_co[j] - t_seed), dT_max)
            else:
                t_seed = self.t_co[j]
            v_prev = self.v_co[j]

        dT_width = int(dT_max / 2)

        mask = np.zeros((vchan,tchan))

        #print(mask.shape)
        #print(mask)
        # disperse each frequency band, and mask
        t_co = np.arange(tchan)
        lin_v_co = lin_func(self.linear, t_co).astype(int)
        valid_v = np.where((lin_v_co >= 0) & (lin_v_co < vchan))
        
        if lin_v_co[0] > lin_v_co[-1]:
            try:
                t_min = valid_v[0][-1]
            except:
                t_min= 0
            try:
                t_max = valid_v[0][0]
            except:
                t_max= 0
        else:
            try:
                t_min = valid_v[0][0]
            except:
                t_min= 0
            try:
                t_max = valid_v[0][-1]
            except:
                t_max= 0

        for t in range(t_min,t_max):
            mask[lin_v_co[t], (t-dT_max):(t+dT_max)] = 1

        #print(mask.shape)
        #print(mask)
        self.lin_mask = mask

    def fit_extrapolate(self, vchan, tchan, tstart, C):
        ''' Runs DM_fit(), lin_fit(), DM_extrapolate(), and lin_extrapolate(). '''
        self.DM_fit(tstart, vchan-1)
        self.lin_fit(C)
        self.DM_extrapolate(vchan, tchan)
        self.lin_extrapolate(vchan, tchan)
        

    def statline(self):
        '''Return a string of the class attributes separated by tabs.'''
        return "%d\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\n" \
                 %(self.N, self.clust_SNR, self.sig_mean, self.sig_max, 
                 self.SNR_mean, self.SNR_max, self.t_range[0],
                 self.t_range[1], self.v_range[0], self.v_range[1], 
                 self.linear[0], self.DM)

# Note: Not used.
def manhattan(x1,x2):
    '''Return the Manhattan distance between two coordinates 
       given by tuples x1 and x2'''
    dist = abs(x1[0]-x2[0]) + abs(x1[1]-x2[1])
    return dist


def avg_time(data, dt):
    ''' Decimate a dynamic spectrum in time (x axis) by averaging together
        sets of <dt> time samples.'''
    (vchan,tchan) = data.shape
    t_num = int(tchan / dt)
    avg_data = np.zeros([vchan,t_num])
    for t in range(t_num):
        t_index = t * dt
        for v in range(vchan):
            avg_data[v,t] = np.mean(data[v,t_index:(t_index+dt)])
    return avg_data


def avg_freq(data, dv):
    ''' Decimate a dynamic spectrum in frequency (y axis) by averaging 
        together sets of <dv> frequency samples.'''
    (vchan,tchan) = data.shape
    v_num = int(vchan / dv)
    avg_data = np.zeros([v_num,tchan])
    for v in range(v_num):
        v_index = v * dv
        for t in range(tchan):
            avg_data[v,t] = np.mean(data[v_index:(v_index+dv),t])
    return avg_data

# Note: Not used.
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

    # Set initial iterates.
    mean_prev = 0.0;
    std_prev = 0.0;
    mean = np.mean(data)
    std = np.std(data)

    # Iteratively compute the background mean and std. dev.
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


# The following two functions are required for scipy.odr regression analysis
def lin_func(beta, x):
    ''' Linear funcion used for orthogonal regression (scipy.odr)'''
    return (beta[0] * x) + beta[1]

def DM_func(beta, v, *args):
    ''' Inverse square function used for DM regression (scipy.odr)'''
    t1 = args[0]
    v1 = args[1]
    return (beta[0] / v**2) + t1 - (beta[0] / v1**2)


def group_clusters(clust_list, data, std, tstart=0.0):

    ''' Group clusters using the DM/lin extrapolation masks. 
        For each cluster in <clust_list>, form a group of other clusters
        that lie inside that cluster's extrapolation masks.
        For each group of clusters, construct a new "super-cluster"
        consisting of the pixels from each cluster in the group. 
        Return a list of the super-clusters.

        Arguments:
            clust_list -- a list of clusters to group
            data -- working dynamic spectrum
            std -- background RMS of the data (computed iteratively)
            tstart -- start time for this set of data
    '''

    # stores tuples containg the indices of clusters in clust_list,
    # so  that the second cluster lies in the first cluster's DM_extrapolate mask
    DM_matches = []
    # same thing but with lin_extrapolate masks
    lin_matches = []

    super_clusters = []

    # FIND MATCHES USING DM/LIN EXTRAPOLATION MASKS
    for c in range(len(clust_list)):
        clust_current = clust_list[c]
        for j in range(len(clust_list)):
            if c != j:
                clust2 = clust_list[j]
                DM_sum = float(np.sum(clust_current.DM_mask[(clust2.v_co, clust2.t_co)]))
                DM_match = DM_sum / clust2.N
                lin_sum = float(np.sum(clust_current.lin_mask[(clust2.v_co, clust2.t_co)]))
                lin_match = lin_sum / clust2.N

                if DM_match > 0.5:
                    DM_matches.append((c,j))
                    #print("DM_sum = " + str(DM_sum))
                    #print("DM_match = " + str(DM_match))
                    #print("Current DM vs. Second DM: " + str(clust_current.DM) + ", " + str(clust2.DM))
                if lin_match > 0.5:
                    lin_matches.append((c,j))

    #print("DM_matches: " + str(DM_matches))

    # FORM SUPER_CLUSTERS, and PUT IN <super_clusters>
    (vchan, tchan) = data.shape
    C = float(vchan) / tchan
    for c in range(len(clust_list)):
        group_indices = [i for i,e in enumerate(DM_matches) if e[0] == c]
        #print(group_indices)
        if len(group_indices) == 0: continue

        group_tco = clust_list[c].t_co
        group_vco = clust_list[c].v_co
        for j in group_indices:
            group_tco = np.append(group_tco, clust_list[DM_matches[j][1]].t_co)
            group_vco = np.append(group_vco, clust_list[DM_matches[j][1]].v_co)
        sigs = data[(group_vco, group_tco)]
        super_cluster = Cluster((group_vco, group_tco), sigs, std)
        # Fit and extrapolate the super_cluster
        super_cluster.fit_extrapolate(vchan, tchan, tstart, C)
        super_clusters.append(super_cluster)

    return super_clusters


def flag_rfi(clust_list, upper, lower):
    ''' Remove clusters in <clust_list> with significantly large/small slopes.

        Arguments:
            clust_list -- list of clusters to flag
            upper -- upper limit on allowed slopes
            lower -- lower limit on allowed slopes

        Return a list of the flagged clusters.
    '''
    removed = []
    for clust in clust_list:
        slope = clust.linear[0]
        if abs(slope) > upper or abs(slope) < lower:
            clust_list.remove(clust)
            removed.append(clust)

    return removed


def fof(gd, data, m1, m2, t_gap, v_gap, tstart, testing_mode, block_mode, block):
  
    global dt
    global dv
    global tsamp
    global vsamp
    global vlow
    global vhigh

    dt = gd['dt']
    dv = gd['dv']
    tsamp = gd['tsamp']
    vsamp = gd['vsamp']
    vlow = gd['vlow']
    vhigh = gd['vhigh']

    import timeit
    start = timeit.default_timer() 

    ''' Perform a friends-of-friends search algorithm.
        Arguments:
            (0) gd --
            (1) data -- raw dynamic spectrum array
            (2) m1 -- single pixel SNR threshold
            (3) m2 -- cluster SNR threshold
            (4) tsamp -- number of time samples to average together
            (5) vsamp -- number of frequency channels to average together
            (6) t_gap -- number of empty time samples allowed...
            (7) v_gap -- number of empty freq. samples allowed... 
                 between pixels in the same cluster
            (8) tstart --
            (9) testing_mode -- 
            (10) block_mode --
            (11) block
    '''
    print("Data Shape: " + str(data.shape))
    #if testing_mode == True:
    plt.imshow(data)
    plt.show()
  
    #flip data along time (axis=1) (not sure why necessary but DM comes out negative if not) 
    data= np.fliplr(data)
 
    print("Computing mean and std.dev. of background noise...")
    (mean,std) = iterative_stats(data, 3, 0.01)

    print("Masking data with single pixel threshold...")
    mask = mask1(data, mean, std, m1)
    (vchan,tchan) = mask.shape
    C = float(vchan) / tchan # used in linear fitting
    
    print("Clustering high signal pixels...")
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
    print("Writing Cluster statistics to text file...")
    clust_list = []
    best_clusters = []
    
    if block_mode == True:
        filename= "block%d_clust_%.1f_%d_%d_%d_%d_%d" %(block,m1,m2,tsamp,vsamp,t_gap,v_gap)
    else:
        filename= "clust_%.1f_%d_%d_%d_%d_%d" %(m1,m2,tsamp,vsamp,t_gap,v_gap)
    f = open(filename + ".txt", "w")
    f.write("fof results, with\nm1=%.2f   m2=%.2f   tsamp=%.2f   vsamp=%.2f   t_gap=%.2f   v_gap=%.2f\n\n" \
            %(m1,m2,tsamp,vsamp,t_gap,v_gap))
    f.write("N \tclust_SNR\t\tsig_mean\tsig_max\t\tSNR_mean\tSNR_max\t\tt_min\t\tt_max\t\t\tv_min\t\tv_max\t\tslope\tDM\n")

    # create cluster objects and add to <clust_list> and write stats to file
    for n in range(num_clusters):
        coords = np.where(labeled_dil==(n+1))
        signals = data[coords]
        new = Cluster(coords,signals,std)
        clust_list.append(new)       
 
        if new.clust_SNR > m2: # CLUSTER FILTER
            # fit and extrapolate
            new.fit_extrapolate(vchan, tchan, tstart, C)
            best_clusters.append(new)
            
            # The four lines below can be uncommented to display
            # individual clusters on the dynamic spectrum.
            #if testing_mode == True:
            #    temp = np.zeros(labeled_dil.shape)
            #    temp[coords] = 1
            #    plt.imshow(temp)
            #    plt.show()
            #    plt.savefig('dynspec' + str(n) + '.png')

            f.write(new.statline())
    
    f.close()


    stop = timeit.default_timer()
    print("Runtime is: " + str(stop-start))
    
    print("Creating clusters plot...")
        
    for clust in clust_list:
        coords = (clust.v_co, clust.t_co)
        labeled_dil[coords] = clust.clust_SNR  

    if testing_mode == False:
       plot(np.fliplr(labeled_dil), save=True, filename=filename)             #plt.savefig(filename + ".png")
    if testing_mode == True:
       plot(np.fliplr(labeled_dil)) 

    print("Finished Search.")

    # flag RFI
    rfi = flag_rfi(best_clusters, vchan/4.0, 10.0/tchan)
    # group high SNR clusters
    print("Creating super clusters (clustering clusters)...")
    super_clusters = group_clusters(best_clusters, data, std, 128.00)

    # create a file containing stats about super clusters
    if block_mode == True:
        super_filename = "block%d_superclust_%.1f_%d_%d_%d_%d_%d" %(block,m1,m2,tsamp,vsamp,t_gap,v_gap)
    else:
        super_filename = "superclust_%.1f_%d_%d_%d_%d_%d" %(m1,m2,tsamp,vsamp,t_gap,v_gap)

    sf = open(super_filename + ".txt", "w")
    sf.write("fof super clusters, with\nm1=%.2f   m2=%.2f   tsamp=%.2f   vsamp=%.2f   t_gap=%.2f   v_gap=%.2f\n\n" \
            %(m1,m2,tsamp,vsamp,t_gap,v_gap))
    sf.write("N \tclust_SNR\t\tsig_mean\tsig_max\t\tSNR_mean\tSNR_max\t\tt_min\t\tt_max\t\t\tv_min\t\tv_max\t\tslope\tDM\n")
    for sc in super_clusters:
        sf.write(sc.statline())    

    # Some plotting
    if testing_mode == True:
        for j in range(len(super_clusters)):
            #clust = best_clusters[j]
            clust = super_clusters[j]
            print(clust.statline())

            ext_mask = 30 * clust.DM_mask
            clust_regions = np.where(labeled_dil > 0)
            super_regions = (clust.v_co, clust.t_co)
            ext_mask[clust_regions] = labeled_dil[clust_regions]
            ext_mask[super_regions] = 200
            #unmasked = np.where(ext_mask==0)
            #ext_mask[unmasked] = labeled_dil[unmasked]
            #plt.imshow(ext_mask)
            #plt.show()


'''
    SORTING FUNCTIONS ---
'''

def open_results(filename):

    f= open(filename)
    lines_list= f.readlines()

    params= lines_list[1]
    stat_names= lines_list[3].split()
    stat_lists= lines_list[4:]
    
    N= len(stat_lists)
    for j in range(N):
        stat_lists[j]= list(map(float, stat_lists[j].split()))

    return (params, stat_names, stat_lists)


def sort_results(stat_lists, stat_names, sort_stat):
    '''
        Sorts the stat_lists according to the statistic specified by sort_stat.
        Returns: sorted stat_lists
        Parameters:
            stat_lists: a list of sublists, each sublist is a line of statistics from
                       a cluster text  file
            stat_names: a list containing the names of statistics, in order
            sort_stat: the name of the statistic to sort by

    '''
    sort_index= stat_names.index(sort_stat)
    stat_lists.sort(reverse= True, key=lambda x:x[sort_index])


def write_sorted(filename, sort_stat):
    '''
        Write a new cluster text file, identical to <filename>, but sorted
        (from high to low) by <sort_stat>
    '''
    (params, stat_names, stat_lists)= open_results(filename)
    sort_results(stat_lists, stat_names, sort_stat)
    
    f = open(filename + "_sorted_%s.txt" %(sort_stat), "w")
    f.write("fof results, with\nm1=%.2f   m2=%.2f   tsamp=%.2f   vsamp=%.2f   t_gap=%.2f   v_gap=%.2f\n\n" \
            %(m1,m2,tsamp,vsamp,t_gap,v_gap))
    f.write("N \tclust_SNR\t\tsig_mean\tsig_max\t\tSNR_mean\tSNR_max\t\tt_min\t\tt_max\t\t\tv_min\t\tv_max\t\tslope\tDM\n")
    for k in range(len(stat_lists)):
        f.write(stat_lists[k])



