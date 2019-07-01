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
            dictionary[x] = remove_spaces(remove_comments(value))
    
    dictionary['methods'] = config.sections()
    
    return dictionary

def remove_comments(value):
    return value.split(";")[0]

def remove_spaces(value):
    temp = value.strip()
    return temp.split()[0]

# convert dictionary string values to float or int if they are numbers
def convert_values(d):
    for x in d:
        if isinstance(d[x], str):
            if is_bool(d[x]):
                d[x] = to_bool(d[x])
            elif is_int(d[x]):
                d[x] = int(d[x])
            elif is_float(d[x]):
                d[x] = float(d[x])
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
    websters = {}
    websters = read_config("Templates/test.cfg")
    
    websters = convert_values(websters)
    
    # Debugging
    print_config(config)
    print("============")
    print(websters)
    
    
    methods = config.sections()
    print("===========")
    print(methods)

