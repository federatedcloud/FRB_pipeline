import numpy as np
import matplotlib.pyplot as plt





def load(filename):
    # filename should be a .npz or .npy file in the current directory
    arr= np.load(filename)


def main(filename):
    arr= load(filename)
    print(arr)
    plt.imshow(arr[0:10,0:10])
    plt.show()

def plot_range(arr, tstart, tend, vstart, vend):
    # tstart, tend, vstart, vend are INDICES
    plt.imshow(arr[tstart:tstart+tend,vstart,vstart+vend])
    plt.show()
