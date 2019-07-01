from method import *
from mi_calc import *

def main(d):
    """
    Calculates the modulation index using the Laura Spitler method.

    Required Parameters:
        directory, basename, mask_dir, mask_name
    """
    print("Calculating modulation index...\n")
    
    directory= d['directory']
    basename= d['basename']
    combined_file= directory + "/single_pulse/" + "%s_MF.sp" %(basename)
    masked_data_file= d['mask_dir'] + d['mask_name']
    output_file= "%s_MF.mi" %(basename)

    t_mi_start = time.time()
    
    combine_sp_files(directory, basename)   # from mi_calc
    
    #cmd = "%s %s %s %s" %(mi_exec, combined_file, masked_data_file, output_file)
    mi_calc.main(combined_file, masked_data_file, ouput_file)   
 
    t_mi_end = time.time()
    dt = t_mi_end - t_mi_start


    return d
