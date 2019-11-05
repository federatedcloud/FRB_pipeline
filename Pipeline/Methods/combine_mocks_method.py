# Method to run combine_mocks within the FRB_pipeline
from method import *

# Required parameters to put in the configuration file are:
#    directory, file1, file2, basename

def main(hotpotato):
    print("Combining 2 fits files")
    
    file1full = get_value(hotpotato, 'directory') + '/' + get_value(hotpotato, 'file1') + '.fits'
    file2full = get_value(hotpotato, 'directory') + '/' + get_value(hotpotato, 'file2') + '.fits'
    fitsname = get_value(hotpotato, 'directory') + '/' + get_value(hotpotato, 'basename')
    
    # do the actual combine
    cmd = "combine_mocks %s %s -o %s" %(file1full, file2full, fitsname)
    try_cmd(cmd)
    
    # rename to basename
    cmd = "mv %s_0001.fits %s.fits" %(fitsname, fitsname)
    try_cmd(cmd)
    
    return hotpotato
