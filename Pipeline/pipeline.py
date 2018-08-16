import sys
sys.path.insert(0, './Methods')
sys.path.insert(0, './Modules')

#import os, time
#import subprocess as sp
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
# TODO: filename should be passed in as an argument and should otherwise run a default.cfg
# default.cfg needs to be set up.  Maybe have it list all possible methods/options?


# Step 2 - TODO: Organize parameters for each method into a dictionary
# This is currently done in the above call to cfg.read_config() and the dictionary is passed in
# but it should be done here so all conversion happens here


# Step 3 - TODO: import method files based on their existence as a section in cfg file


# Step 4 - If combine_mocks method is defined, call it first
if hotpotato['combine']:
    import combine_mocks_method as combine
    combine.main(hotpotato)


# Step 5 - create a dynamic spectra as numpy array
import fits2npz_method as f2n
hotpotato = f2n.main(hotpotato)


# Step 6 - Call FOF method
import FOF_method as FOF
hotpotato = FOF.main(hotpotato)


# Step 7 - Exit cleanly
# TODO: remove combined file?
sys.exit("\n Pipeline tasks completed \n=====")






# Optional Steps
#  Timer class
#  Check dependencies
#  Basic error checking of config
#  Error checking of methods







