# Method to organize results and output
from method import *


def main(hotpotato):
    print("Organizing output files")
   
    params_list= ['directory', 'output_directory', 'mask_dir', 'move_npz_file', 
                  'move_combined_file', 'move_maskdata_file', 'filename_npz'
                  'basename', 'filfile']
    print_params(params_list)
     
    data_dir = get_value(hotpotato, 'directory')
    mask_dir = get_value(hotpotato, 'mask_dir')
    results_dir = get_value(hotpotato, 'output_directory')
    
    # Move generated .npz file
    if (get_value(hotpotato, 'move_npz_file') == True):
        if (get_value(hotpotato, 'output_npz_file') == False):
            print("No .npz file output to move, skipping.")
        else:
            cmd = "mv %s.npz %s" %(get_value(hotpotato, 'filename_npz'), results_dir)
            try_cmd(cmd)
    
    # Move generated combined .fits file
    if (get_value(hotpotato, 'move_combined_file') == True):
        cmd = "mv %s/%s.fits %s" %(get_value(hotpotato, 'directory'), get_value(hotpotato, 'basename'), results_dir)
        try_cmd(cmd)
    
    # Move filterbank file
    if (get_value(hotpotato, 'move_maskdata_file') == True):
        cmd = "mv %s/%s %s/masked_dynamic_spectra.fil" %(data_dir, get_value(hotpotato, 'filfile'), results_dir)
        try_cmd(cmd)

# TODO: rewrite this based on https://stackoverflow.com/questions/21804935/how-to-use-the-mv-command-in-python-with-subprocess    
#    # Move generated text files
#    if (get_value(hotpotato, 'move_txt_files') == True):
#        cmd = "mv *.txt %s" %(results_dir)
#        try_cmd(cmd)
#    
#    # Move generated png files
#    if (get_value(hotpotato, 'move_png_files') == True):
#        cmd = "mv *.png %s" %(results_dir)
#        try_cmd(cmd)
    
    
    # Insert more move commands in here as needed to organize results
    
    return hotpotato

