# Module for parallel processing options
import importlib
from multiprocessing import *

# A test function
def test(x):
    print(current_process())
    return x*x

def run_method_list(hotpotato):
    x = hotpotato['method_list']
    n = hotpotato['num_methods']
    print(x)
    for i in range(0, n):
        run_method(x[i], hotpotato)
        #temp = __import__(x[i] + '_method')
        #hotpotato = temp.main(hotpotato)

def run_method(method, hotpotato):
    temp = __import__(method + '_method')
    return temp.main(hotpotato)

