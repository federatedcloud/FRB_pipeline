# Method to print "Hello World!"
from method import *


def main(hotpotato):
    total = int(get_value(hotpotato, 'print_count'))
    
    if (total > 1):
        for x in range(0,total):
            print("Hello World!\n")
    else:
        print("Hello World!\n")
    
    return hotpotato
