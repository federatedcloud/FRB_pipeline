import numpy as np
import matplotlib.pyplot as plt





def load(filename):
    # filename should be a .npz or .npy file in the current directory
    arr= np.load(filename)


def basic_plot_go(arr):
    print("Image has dimesions: " + arr.shape)
    plt.imshow(arr)
    plt.show()

def plot_range(arr, tstart, tend, vstart, vend):
    # tstart, tend, vstart, vend are INDICES
    plt.imshow(arr[tstart:tstart+tend,vstart,vstart+vend])
    plt.show()
