# Execution of pipeline happens here

import sys
sys.path.insert(0, './Methods')
sys.path.insert(0, './Modules')

import argparse
import importlib
import readconfig as cfg


# Set up command-line parser
cmdparser = argparse.ArgumentParser()
cmdparser.add_argument("configpath",
                        help="Path to configuration file (.cfg); defaults to using Templates/default.cfg",
                        nargs='?',
                        default="Templates/default.cfg")
args = cmdparser.parse_args()
if args.configpath == "Templates/default.cfg":
    print("No configuration file was selected; using " + args.configpath)

print("=====\n Pipeline started\n")

# Genreal-purpose dictionary that gets passed everywhere
hotpotato = {}

# Read the config file
hotpotato = cfg.read_config(args.configpath)

# Step 2 - TODO: Ensure proper conversion of config file parameters when added to dictionary
# This is currently done in the method files, but all conversion should happen here


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

