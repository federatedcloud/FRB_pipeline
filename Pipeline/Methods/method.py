import sys, time
import subprocess as sp
sys.path.insert(0, '../Modules')

# TODO: method class
#class method:
#    def __init__(self):
        

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

# Save dynamic spectra and headers as .npz file
def save_npz(npzfilename, dynamic_spectra, primary_header, subint_header):
    print("Writing numpy array to disk...\n")
    
    if (npzfilename == ""):
        npzfilename = "output_dynamic_spectra"
    
    np.savez(npzfilename, dynamic_spectra, primary_header, subint_header);
    
    print("Write complete.")
    return

