# Method to run the same method on multiple chunks of data
from method import *
from multiprocessing import Pool
import parallel as para


def main(hotpotato):
    params_list = ['num_proc', 'method_list']
    print_params(params_list)
    
    # prepare variables
    p = Pool(get_value(hotpotato, 'num_proc'))
    newlist = get_value(hotpotato, 'method_list')
    #print(newlist)
    method_list = [None] * get_value(hotpotato, 'num_methods')
    for i in range(0, get_value(hotpotato, 'num_methods')):
        method_list[i] = newlist.split(",")[0]
    #print(method_list)
    set_value(hotpotato, 'method_list', method_list)
    
    #if (get_value(hotpotato, 'testing_mode')):
    #    print(p.map(para.test, range(get_value(hotpotato,'test_num'))))
    
    # do parallel stuff here
    p.map(para.run_method_list, hotpotato) #TODO: Make this work?
    #para.run_method_list(hotpotato)
    
    return hotpotato

