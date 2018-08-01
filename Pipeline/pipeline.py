import sys
sys.path.insert(0, './Methods')
sys.paht.insert(0, './Modules')

#import os, time
#import subprocess as sp
import readconfig as cfg
from optparse import OptionParser

# Methods
import combine_mocks_method as combine
import FOF_method as FOF
import fits2npz_method as f2n

# Below copied from mod_sp.py
#def main():
#    parser = OptionParser(usage)
#    parser.add_option("-f" ...


print("=====\n Pipeline started\n")

# Set up the genreal-purpose dictionary that gets passed everywhere
#hotpotato = {}
# TODO: default values?


# Step 1 - Read the config file
hotpotato = cfg.read_config("Templates/simpleFOF.cfg")
# TODO: filename should be passed in as an argument and should otherwise run a default.cfg
# default.cfg needs to be set up.  Maybe have it list all possible methods/options?


# Step 2 - TODO: Organize parameters for each method into a dictionary
# This is currently done in the above call to cfg.read_config() and the dictionary is passed in
# but it should be done here so all conversion happens here


# Step 3 - TODO: import method files based on their existence as a section in cfg file


# Step 4 - If combine_mocks method is defined, call it first

combine.main(hotpotato)


# Step 4 - 
# TODO: create a dynamic spectra as numpy array
hotpotato = f2n.main(hotpotato)


# Step 5 - Call FOF method
hotpotato = FOF.main(hotpotato)

# Step 5 - Exit cleanly
# TODO: remove combined file?
sys.exit("Pipeline tasks completed\n =====")






# Optional Steps
#  Timer class
#  Check dependencies
#  Basic error checking of config
#  Error checking of methods






