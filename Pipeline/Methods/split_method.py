from method import *
import numpy as np
import os
import sys
from glob import glob

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
    bandpass_name= get_value(hotpotato, 'bandpass_name')
    npz_name= get_value(hotpotato, 'npz_name')
    if not os.path.exists(split_dir):
        os.makedirs(split_dir)


    if bandpass_name != '':
        filelist= glob('%s*.npy' %(bandpass_name))
        # Note that each bandpass-corrected segment has the same time dimension
    else:
        filelist= [npz_name + '.npz']
    
    print(filelist)
    # save each block to a .npy file in split_dir, and
    # pass a list of the npy file names to hotpotato
    
    seg0= filelist[0]
    if seg0[-4:] == '.npz':
        npzfile= np.load(seg0)
        ar0= npzfile[npzfile.files[0]]
    elif seg0[-4:] == '.npy':
        ar0= np.load(seg0)
    else:
        print('Wrong file extension: must be either .npz or .npy. Quitting...')
        sys.exit()

    DT= ar0.shape[1]
    block_list= []

    for seg in filelist:
        # Get Data file
        if seg[-4:] == '.npz':
            npzfile= np.load(seg)
            ar= npzfile[npzfile.files[0]]
        elif seg[-4:] == '.npy':
            ar= np.load(seg)
        else:
            print('Wrong file extension: must be either .npz or .npy. Quitting...')
            break
        # Now split the data
        n= 0
        counter= 0
        while n < DT:
            if n + block_size < DT:
                block= ar[:,n:n+block_size]
            else:
                block= ar[:,n:]
            if bandpass_name != '':
                block_name= 'block%d_%d_%d_%s.npy' %(counter, n, block_size, seg[:-4])
            else:
                block_name= 'block%d_%d_%d.npy' %(counter, n, block_size)
            block_list.append(block_name)
            np.save(split_dir + '/' + block_name, block)
            n+= (block_size - overlap)
            counter+= 1

    print("Finishing splitting the array.")

    hotpotato['split_list']= block_list
    return hotpotato
