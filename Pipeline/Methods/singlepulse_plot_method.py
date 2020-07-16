from method import *
import bisect, os, sys, getopt, infodata, glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from scipy import *
from singlepulse_plot import *

#Required parameters to put in the configuration file are:
#  sp_directory, threshold
#Note: other parameters are obtained from header files (stored in hotpotato)

def main(hotpotato):
    params_list= ['sp_directory, threshold']
    print_params(params_list)

    print("Making singlepulse plots")

    sp_directory= get_value(hotpotato, 'sp_directory')
    threshold= get_value(hotpotato, 'threshold')
    make_singlepulse_plot(sp_directory, threshold)

    return hotpotato 
