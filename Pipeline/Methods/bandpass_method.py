from method import *
from bandpass import *
import numpy as np

# Required parameters to put in the configuration file are:
#   directory, basename, mask_dir, filfile, output_npz_file, npz_name, NCHAN, TBIN
# Note: other parameters are obtained from header files (stored in hotpotato)

def main(hotpotato):
    print("Removing bandpass.")

    # Note: methods should always be in config file
    params_list= ['methods', 'directory', 'npz_name', 'min_chans']
    print_params(params_list)

    directory= get_value(hotpotato, 'directory') 
    npz_name= get_value(hotpotato, 'npz_name')
    min_chans= get_value(hotpotato, 'min_chans')
    bandpass_name= get_value(hotpotato, 'bandpass_name')

    npz_file= np.load(npz_name + '.npz')
    npz_array= npz_file[npz_file.files[0]]

    print('npz_array shape: ' + str(npz_array.shape))
    npz_bandpass= calc_median_bandpass(npz_array)
    print('npz_bandpass shape: ' + str(npz_bandpass.shape))
    dd= correct_bandpass(npz_array, npz_bandpass)
    print('dd shape: ' + str(dd.shape))

    # SPLIT DATA INTO CHUNKS AROUND BAD CHANNELS (nans)
    # 1 == True means a number, 0 means a nan
    Nv, Nt= dd.shape
    nan_chans= np.ones((Nv,1))
    data_ranges= []

    start= 0
    prev= 0
    for j in range(Nv):
        if np.any(np.isnan(dd[j,:])) == True:
            nan_chans[j]= 0
            if prev == 1 and (j - start > min_chans):
                data_ranges.append((start, j-1))
            prev= 0
        else:
            if prev == 0:
                start= j
            if j == Nv-1 and (j - start > min_chans):
                data_range.append(start, j)
            prev= 1

    print(data_ranges)

    print('Saving band-pass-corrected DS, avoiding nans as .npy')
    for pair in data_ranges:
        np.save(bandpass_name + '_chans%dto%d.npy' %(pair[0], pair[1]), dd[pair[0]:pair[1]+1,:])
    
    return hotpotato
