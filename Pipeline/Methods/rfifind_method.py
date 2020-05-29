from method import *

def main(hotpotato):

    print("Running PRESTO rfifind")
    t_rfi_start = time.time()
   
    params_list= ['directory', 'rfi_dir', 'basename', 'rfi_flags', 'rfi_otherflags']
    print_params(params_list)
 
    # get/set file locations
    directory= get_value(hotpotato, 'directory')
    rfi_dir = get_value(hotpotato, 'rfi_dir')
    basename = get_value(hotpotato, 'basename')
    fitslist = glob('%s/%s*.fits' %(directory, basename))
    fitslist.sort()
    fitsfiles = ' '.join(fitslist)
    
    # get parameters from dictionary
    rfi_flags = get_value(hotpotato, 'rfi_flags')
    rfi_otherflags = get_value(hotpotato, 'rfi_otherflags') + ' '
    
    # run command    
    cmd = 'rfifind -o %s %s %s %s' %(basename, rfi_flags, rfi_otherflags, fitsfiles)
    try_cmd(cmd)
   
    # move products to rfi_products directory 
    if not os.path.exists(rfi_dir):
        os.makedirs(rfi_dir)

    cmd = 'mv ./*rfifind.* ' + rfi_dir
    try_cmd(cmd)
    
    t_rfi_end = time.time()
    rfi_time = (t_rfi_end - t_rfi_start)
    print("RFI Flagging took %f seconds" %(rfi_time))
    
    return hotpotato
