import sys
import configparser
from collections import OrderedDict

config = configparser.SafeConfigParser(dict_type=OrderedDict, allow_no_value=True)

def print_config(config):
    for x in config.sections():
        print("[%s]"%(x))
        for(x, value) in config.items(x):
            print("%s=%s"%(x,value))
        print()

def read_config(filename, dictionary={}):
    config.read(filename)
    
    # Check if data is the first section
    if not ('data' in config.sections()):
        sys.exit("Error: the selected configuration file does not contain the "
            "[data] section, which is necessary.  Quitting.\n")
    
    # Put information in the dirctionary
    for x in config.sections():
        for(x, value) in config.items(x):
            dictionary[x] = remove_comments(value)
    
    dictionary['methods'] = config.sections()
    
    return dictionary

def remove_comments(value):
    return value.split(" ")[0]


####################
##     MAIN       ##
####################

if __name__ == "__main__":
    websters = {}
    websters = read_config("Templates/default.cfg")
    
    # Debugging
    print_config(config)
    print("============")
    print(websters)
    
    
    methods = config.sections()
    print("===========")
    print(methods)

