from method import *
import numpy as np
import os

# Splits a Dynamic Spectrum (Numpy Array) into many smaller Arrays
# Inputs: .npz file with single array
# Ouputs: .npz file with several smaller arrays

def main(hotpotato):

    print("Splitting .npz array into blocks.")
    print("Loading .npz file.")
    
    params_list= ['npz_name', 'block_size', 'overlap', 'split_dir']
    print_params(params_list)

    # get parameters from hot potato
    block_size= int(get_value(hotpotato, 'block_size'))     # bins
    overlap= int(get_value(hotpotato, 'overlap'))           # bins
    split_dir= get_value(hotpotato, 'split_dir')
    if not os.path.exists(split_dir):
        os.makedirs(split_dir)   

    npzfile= np.load(get_value(hotpotato, 'npz_name') + '.npz')
    npzlist= npzfile.files
    ar= npzfile[npzlist[0]]
    DV, DT= ar.shape
    
    # save each block to a .npy file in split_dir, and
    # pass a list of the npy file names to hotpotato
    n= 0
    counter= 0
    block_list= []
    while n < DT:
        if n + block_size < DT:
            block= ar[:,n:n+block_size]
        else:
            block= ar[:,n:]
        block_name= 'block%d_%d_%d.npy' %(counter, n, block_size)
        block_list.append(block_name)
        np.save(split_dir + '/' + block_name, block)
        n+= (block_size - overlap)
        counter+= 1

    print("Finishing splitting the array.")

    hotpotato['split_list']= block_list
    return hotpotato
