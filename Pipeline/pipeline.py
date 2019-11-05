#!/usr/bin/env python3

import sys
sys.path.insert(0, './Methods')
sys.path.insert(0, './Modules')

import argparse
import importlib
import readconfig as cfg

from method import *

true_values = ['True', 'true', 'TRUE', 'T', 't']
false_values = ['False', 'false', 'FALSE', 'F', 'f']

# Execution of pipeline happens here
def main():
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
    
    # Ensure proper conversion of config file and header parameters in dictionary
    hotpotato = cfg.convert_values(hotpotato)
    
    # Dynamically import and call the main function of each method defined in cfg
    for x in get_value(hotpotato, 'methods'):
        if (x == 'data'):
            continue
        temp = __import__(x + '_method')
        hotpotato = temp.main(hotpotato)
    
    # Exit cleanly
    sys.exit("\n Pipeline tasks completed \n=====")
    
    #===============================
    # Optional Steps
    #  Timer class
    #  Check dependencies
    #  Basic error checking of config
    #  Error checking of methods
    #===============================



####################
##     MAIN       ##
####################

if __name__ == "__main__":
    main()

