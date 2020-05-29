from method import *
from mi_calc import *

def main(hotpotato):
    """
    Calculates the modulation index using the Laura Spitler method.

    Required Parameters:
        directory, basename, mask_dir, mask_name
    """
    print("Calculating modulation index...\n")

    params_list= ['directory', 'basename', 'mask_dir', 'mask_name']
    print_params(params_list)
    
    directory= get_value(hotpotato, 'directory')
    basename= get_value(hotpotato, 'basename')
    combined_file= directory + "/single_pulse/" + "%s_MF.sp" %(basename)
    masked_data_file= get_value(hotpotato, 'mask_dir') + get_value(hotpotato, 'mask_name')
    output_file= "%s_MF.mi" %(basename)

    t_mi_start = time.time()
    
    combine_sp_files(directory, basename)   # from mi_calc
    
    #cmd = "%s %s %s %s" %(mi_exec, combined_file, masked_data_file, output_file)
    mi_calc.main(combined_file, masked_data_file, ouput_file)   
 
    t_mi_end = time.time()
    dt = t_mi_end - t_mi_start


    return hotpotato
