#import os, sys, time
#import subprocess as sp
import readconfig as cfg
import numpy as np
from optparse import OptionParser


# Below copied from mod_sp.py
#def main():
#    parser = OptionParser(usage)
#    parser.add_option("-f" ...


# Set up the genreal-purpose dictionary that gets passed everywhere
hotpotato = {}
# TODO: default values?


# Step 1 - Read the config file
cfg.read_config(filename="Templates/simpleFOF.cfg", dictionary=hotpotato)
# TODO: filename should be passed in as an argument and should otherwise run a default.cfg
# default.cfg needs to be set up.  Maybe have it list all possible methods/options?


# Step 2 - Organize parameters for each method into a dictionary



# Step 3 - Call each method with dictionary
# TODO: create a combine_mocks "method"
# TODO: create a dynamic spectra as numpy array
# TODO: organize/use FOF method Plato made


# Step 4 - Exit cleanly








# Optional Steps
#  Timer class
#  Check dependencies
#  Basic error checking of config
#  Error checking of methods
#  






