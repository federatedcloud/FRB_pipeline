# modulation index calculation
from method import *

import time


def main(hotpotato):
    """
    Calculates the modulation index using the Laura Spitler method.
    """
    print("Calculating modulation index...\n")
    
    data_dir = get_value(hotpotato, 'directory')
    work_dir= get_value(hotpotato, 'dictionary')
    basename= get_value(hotpotato, 'basename')
    t_mi_start = time.time()
   
    # combine_sp_files(work_dir, basename) --
    """
    Combines all the .singlepulse files from the single_pulse_search into a single .sp file
    that the modulation index calculation is expecting.
    """
    print("Combining .singlepulse files...\n")
    t_awk_start = time.time()
    sp_dir = work_dir
    
    awk_cmd = """awk '$1!="#" {print}' %s_DM*.singlepulse > %s_MF.sp""" %(basename, basename)
    cmd = "(pushd %s && %s; popd)" %(sp_dir, awk_cmd) # run command in sp_dir
    try_cmd(cmd)
    
    t_awk_end = time.time()
    print("Combining .singlepulse files took %.2f seconds" %(t_awk_end-t_awk_start))

    # Continue with modulation index calcultion.
    mi_exec = get_value(hotpotato, 'mi_exec')
    combined_file = work_dir + "%s_MF.sp" %(basename)
    maskname = 'raw_data_with_mask'
    masked_data_file = data_dir + "/%s.fits" %(maskname)
    output_file = "%s_MF.mi" %(basename)
    
    cmd = "%s %s %s %s" %(mi_exec, combined_file, masked_data_file, output_file)
    try_cmd(cmd)
   
    t_mi_end = time.time()
    print("Modulation Index calculation took %.2f seconds" %(t_mi_end-t_mi_start))
    return hotpotato
