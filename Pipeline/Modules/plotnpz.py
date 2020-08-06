import numpy as np
import matplotlib.pyplot as plt

'''
A quick and esay method for plotting a dynamic spectrum in numpy array format

Parameters:
    data -- a 2D numpy array representing a dynamic spectrum
    save -- boolean value determining whether plot is shown or saved (default False)
    filename -- basename for saved plot
    vmin -- lower end of colorbar normalization (default None) [read more in the matplotlib docs]
    vmax -- upper end of colorbar normalization (default None)
'''
def plot(data, save=False, filename=None,vmin=None, vmax=None):
    plt.imshow(data, aspect='auto', origin='lower',vmin=vmin, vmax=vmax)
    plt.xlabel('Time sample (#)', fontsize=14)
    plt.ylabel('Frequency sample (#)', fontsize=14)
    h = plt.colorbar()
    h.set_label('Flux density (arbitrary units)', fontsize=14)
    if not save:
        plt.show()
    else:
        plt.savefig(filename+'.png')

