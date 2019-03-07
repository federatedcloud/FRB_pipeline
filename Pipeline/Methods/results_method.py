# Method to organize results and output
from method import *


def main(dictionary):
    print("Organizing output files")
    
    results_dir = dictionary['output_directory']
    
    # Move generated .npz file
    if (dictionary['move_npz_file'] == True):
        cmd = "mv %s.npz %s" %(dictionary['filename_npz'], results_dir)
        try_cmd(cmd)
    
    # Move generated combined .fits file
    if (dictionary['move_combined_file'] == True):
        cmd = "mv %s.fits %s" %(dictionary['fitsname'], results_dir)
        try_cmd(cmd)
        
    
    # Insert more move commands in here as needed to organize results
    
    return dictionary

