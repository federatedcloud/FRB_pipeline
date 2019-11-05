from method import *
import numpy as np
import os

# Splits a Dynamic Spectrum (Numpy Array) into many smaller Arrays
# Inputs: .npz file with single array
# Ouputs: .npz file with several smaller arrays

def main(hotpotato):

    print("Loading .npz file.")
    
    params_list= ['npz_name', 'block_size', 'overlap', 'split_dir']
    print_params(params_list)

    npzfile= np.load(get_value(hotpotato, 'npz_name') + '.npz')
    npzlist= npzfile.files
    
    # get parameters from hot potato
    ar= npzfile[npzlist[0]]
    DV, DT= ar.shape
    block_size= int(get_value(hotpotato, 'block_size'))     # bins
    overlap= int(get_value(hotpotato, 'overlap'))           # bins
    split_dir= get_value(hotpotato, 'split_dir')
    if not os.path.exists(split_dir):
        os.makedirs(split_dir)   

    # save each block to a .npy file in split_dir
    n= 0
    counter= 0
    while n < DT:
        if n + block_size < DT:
            block= ar[:,n:n+block_size]
        else:
            block= ar[:,n:]
        n2= block_size - overlap    
        np.save('%s/block_%d_%d_%d' %(split_dir, counter, n, n2), block)
        n+= n2    
        counter+= 1

    print("Finishing splitting the array.")

    return hotpotato
