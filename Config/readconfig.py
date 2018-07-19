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
    
    
    # Put information in the dirctionary
    for x in config.sections():
        for(x, value) in config.items(x):
            dictionary[x] = value
    
    return dictionary




####################
##     MAIN       ##
####################

if __name__ == "__main__":
    websters = {}
    read_config("Templates/simpleFOF.cfg", websters)
    
    print_config(config)
    print("============")
    print(websters)
    
    
    #methods = config.sections()


