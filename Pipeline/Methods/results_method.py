# Method to organize results and output
from method import *


def main(d):
    print("Organizing output files")
    
    data_dir = d['directory']
    results_dir = d['output_directory']
    
    # Move generated .npz file
    if (d['move_npz_file'] == True):
        if (d['output_npz_file'] == False):
            print("No .npz file output to move, skipping.")
        else:
            cmd = "mv %s.npz %s" %(d['filename_npz'], results_dir)
            try_cmd(cmd)
    
    # Move generated combined .fits file
    if (d['move_combined_file'] == True):
        cmd = "mv %s/%s.fits %s" %(d['directory'], d['basename'], results_dir)
        try_cmd(cmd)
    
    # Move filterbank file
    if (d['move_maskdata_file'] == True):
        cmd = "mv %s/%s %s/masked_dynamic_spectra.fil" %(data_dir, d['filename_fil'], results_dir)
        try_cmd(cmd)

# TODO: rewrite this based on https://stackoverflow.com/questions/21804935/how-to-use-the-mv-command-in-python-with-subprocess    
#    # Move generated text files
#    if (d['move_txt_files'] == True):
#        cmd = "mv *.txt %s" %(results_dir)
#        try_cmd(cmd)
#    
#    # Move generated png files
#    if (d['move_png_files'] == True):
#        cmd = "mv *.png %s" %(results_dir)
#        try_cmd(cmd)
    
    
    # Insert more move commands in here as needed to organize results
    
    return d

