# Execution of pipeline happens here

import sys
sys.path.insert(0, './Methods')
sys.path.insert(0, './Modules')

#import os, time
#import subprocess as sp
import importlib
import readconfig as cfg
from optparse import OptionParser


# Below copied from mod_sp.py
#def main():
#    parser = OptionParser(usage)
#    parser.add_option("-f" ...


print("=====\n Pipeline started\n")

# Set up the genreal-purpose dictionary "hotpotato" that gets passed everywhere
hotpotato = {}


# Step 1 - Read the config file
hotpotato = cfg.read_config("Templates/simpleFOF.cfg")
#hotpotato = cfg.read_config()

# TODO: filename should be passed in as an argument and should otherwise run a default.cfg


# Step 2 - TODO: Organize parameters for each method into a dictionary
# This is currently done in the above call to cfg.read_config() and the dictionary is passed in
# but it should be done here so all conversion happens here


# Step 3 - If combine_mocks method is defined, call it first
if 'combine_mocks' in hotpotato['methods']:
    # TODO: error check this
        #if ((not cfg.config.has_option('file1')) or (not cfg.config.has_option('file2'))):
        #    sys.exit("\n Error: Configuration file is not set up correctly:"
        #               " combine = True but file1 and file2 are not properly defined") 
        #elif ((hotpotato['file1'] == '') and (hotpotato['file2'] == '')):
        #    sys.exit("\n Error: Configuration file is not set up correctly:"
        #               " combine = True but file1 and file2 are not properly defined")
    
    combine = __import__('combine_mocks' + '_method')
    combine.main(hotpotato)


# Step 4 - create a dynamic spectra as numpy array
if hotpotato['use_np_array']:
    import fits2npz_method as f2n
    hotpotato = f2n.main(hotpotato)


# Step 5 - dynamically import and call the main function of each method defined in cfg
for x in hotpotato['methods']:
    if (x == 'data' or x == 'combine_mocks'):
        continue
    temp = __import__(x + '_method')
    temp.main(hotpotato)


# Step 6 - Exit cleanly
# TODO: remove combined file?
sys.exit("\n Pipeline tasks completed \n=====")


# Optional Steps
#  Timer class
#  Check dependencies
#  Basic error checking of config
#  Error checking of methods

