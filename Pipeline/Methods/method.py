import sys, time
import subprocess as sp
import numpy as np
sys.path.insert(0, '../Modules')


def get_value(hotpotato, key):
    return hotpotato.get(key,'')

def set_value(hotpotato, key, value):
    hotpotato[key] = value
    return

def try_cmd(cmd, stdout=None, stderr=None):
    # Run the command in the string cmd using sp.check_call()
    # If there is a problem running, a CalledProcessError will occur
    # and the program will quit.
    print("\n\n %s \n\n" %cmd)
    
    try:
        retval = sp.check_call(cmd, shell=True, stdout=stdout, stderr=stderr,
                                executable='/bin/bash')
    except sp.CalledProcessError:
        sys.exit("%s \n The above command did not work, quitting.\n" %cmd)


def print_params(param_list):
    # Print a list of required parameters. The list is constructed in individual method files.
    params_string= 'The following parameters must be specified in the configuration file to call this method:\n'
    for param in param_list:
        params_string+= param + ', '
    print('\n' + params_string + '\n')


def print_fits_params(param_list):
    # Print a list of parameters that must be pulled from a FITS header.
    params_string= 'The following parameters must be pulled from a FITS file header, or specified in the configuration file:\n'
    for param in param_list:
        params_string+= param + ', '
    print('\n' + params_string + '\n')


def save_npz(npzfilename, dynamic_spectra):
    # Save dynamic spectra and headers as .npz file
    print("Writing numpy array to disk...\n")
    
    if (npzfilename == ""):
        npzfilename = "output_dynamic_spectra"
    
    np.savez(npzfilename, dynamic_spectra);
    
    print("Write complete.")
    return


def read_npz(npzfilename, array_index=0):
    '''
    Read a .npz file into a numpy array
    Return: numpy array
    Return the array_index(th) array in npzfilename
    '''
    print("Reading .npz file into numpy array")
    npzfile= np.load(npzfilename + '.npz')
    files_list= npzfile.files
    return npzfile[files_list[array_index]]
