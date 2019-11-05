# Method to print "Hello World!"
from method import *


def main(hotpotato):

    params_list= ['print_count']
    print_params(params_list)
    total = int(get_value(hotpotato, 'print_count'))
    
    if (total > 1):
        for x in range(0,total):
            print("Hello World!\n")
    else:
        print("Hello World!\n")
    
    return hotpotato
