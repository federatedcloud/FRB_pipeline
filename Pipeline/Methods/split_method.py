
from method import *
import numpy as np
import os

# Splits a Dynamic Spectrum (Numpy Array) into many smaller Arrays
# Inputs: .npz file with single array
# Ouputs: .npz file with several smaller arrays

def main(d):

    print("Loading .npz file.")
    npzfile= np.load(d['npz_name'] + '.npz')
    print(npzfile)
    npzlist= npzfile.files
    print(npzlist)
    print(len(npzlist))
    
    # get parameters from hot potato
    ar= npzfile[npzlist[0]]
    print(ar.shape)
    DV, DT= ar.shape
    block_size= int(d['block_size'])     # bins
    overlap= int(d['overlap'])           # bins
    split_dir= d['split_dir'].split()[0]
    if not os.path.exists(split_dir):
        os.makedirs(split_dir)   

    print('block_size= ' + str(block_size))
    print('overlap= ' + str(overlap)) 
    print('DV, DT= ' + str(DV) + ', ' + str(DT))

    # save each block to a .npy file in split_dir
    n= 0
    counter= 0
    while n < DT:
        print(n)
        if n + block_size < DT:
            block= ar[:,n:n+block_size]
        else:
            block= ar[:,n:]
        n2= block_size - overlap    
        np.save('%s/block_%d_%d_%d' %(split_dir, counter, n, n2), block)
        n+= n2    
        counter+= 1

    print("Finishing splitting the array.")

    return(d)
