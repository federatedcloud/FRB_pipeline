import sys
import configparser
from collections import OrderedDict

true_values = ['True', 'true', 'TRUE', 'T', 't']
false_values = ['False', 'false', 'FALSE', 'F', 'f']

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
            if (is_bool(value)):
                #print("something is a bool")
                dictionary[x] = to_bool(remove_spaces(value))
            else:
                dictionary[x] = remove_comments(value)
    
    dictionary['methods'] = config.sections()
    
    return dictionary

def remove_comments(value):
    return value.split(";")[0]

def remove_spaces(value):
    return value.split()[0]

# check if input can be converted to bool, return bool (of if it can)
def is_bool(input):
    if ((remove_spaces(input) in true_values) or (remove_spaces(input) in false_values)):
        return True
    else:
        return False

def to_bool(input):
    if input in true_values:
        return True
    else:
        return False



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

