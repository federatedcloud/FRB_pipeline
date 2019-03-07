# Method to run combine_mocks within the FRB_pipeline
from method import *


def main(dictionary):
    print("Combining 2 fits files")
    
    file1full = dictionary['directory'] + '/' + dictionary['file1'] + '.fits'
    file2full = dictionary['directory'] + '/' + dictionary['file2'] + '.fits'
    fitsname = dictionary['directory'] + '/' + dictionary['basename']
    
    # do the actual combine
    cmd = "combine_mocks %s %s -o %s" %(file1full, file2full, fitsname)
    try_cmd(cmd)
    
    # rename to basename
    cmd = "mv %s_0001.fits %s.fits" %(fitsname, fitsname)
    try_cmd(cmd)
    
    return dictionary
