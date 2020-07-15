from method import *
import bisect, os, sys, getopt, infodata, glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from scipy import *
from singlepulse_plot import *

#Required parameters to put in the configuration file are:
#  sp_directory
#Note: other parameters are obtained from header files (stored in hotpotato)

def main(hotpotato):
    print("Making singlepulse plots")

    params_list= ['sp_directory']
    print_params(params_list)

    sp_directory= get_value(hotpotato, 'sp_directory')
    make_singlepulse_plot(sp_directory)

    return hotpotato 
