import sys, time
import subprocess as sp

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

