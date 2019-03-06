# Execution of pipeline happens here

import sys
sys.path.insert(0, './Methods')
sys.path.insert(0, './Modules')

import argparse
import importlib
import readconfig as cfg

true_values = ['True', 'true', 'TRUE', 'T', 't']
false_values = ['False', 'false', 'FALSE', 'F', 'f']

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
    hotpotato = convert_values(hotpotato)
    
    # If combine_mocks method is defined, call it first
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
    
    # Create a dynamic spectra as numpy array
    if (hotpotato['use_np_array'] == True):
        import fits2npz_method as f2n
        hotpotato = f2n.main(hotpotato)
    
    # Dynamically import and call the main function of each method defined in cfg
    for x in hotpotato['methods']:
        if (x == 'data' or x == 'combine_mocks'):
            continue
        temp = __import__(x + '_method')
        temp.main(hotpotato)
    
    # Exit cleanly
    # TODO: remove combined file?
    sys.exit("\n Pipeline tasks completed \n=====")
    
    #===============================
    # Optional Steps
    #  Timer class
    #  Check dependencies
    #  Basic error checking of config
    #  Error checking of methods
    #===============================


# convert dictionary string values to float or int if they are numbers
def convert_values(d):
    for x in d:
        if isinstance(d[x], str):
            if is_bool(d[x]):
                d[x] = to_bool(d[x])
            elif is_float(d[x]):
                d[x] = float(d[x])
            elif is_int(d[x]):
                d[x] = int(d[x])
            else:
                continue
    
    return d

# check if input can be converted to bool, return bool (of if it can)
def is_bool(input):
    if ((input in true_values) or (input in false_values)):
        return True
    else:
        return False

def to_bool(input):
    if input in true_values:
        return True
    else:
        return False

# check if input can be converted to float, return bool
def is_float(input):
    try:
        n = float(input)
    except ValueError:
        return False
    
    return True

# check if input can be converted to int, return bool
def is_int(input):
    try:
        n = int(input)
    except ValueError:
        return False
    
    return True


####################
##     MAIN       ##
####################

if __name__ == "__main__":
    main()

