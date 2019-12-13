from method import *

# Map file types to their corresponding extensions.
# TODO: add to method.py and use in other methods where it's useful
file_extensions = {'psrfits':'.fits','filterbank':'.fil'}

def main(hotpotato):

    print('\nDetermining velocity for barycentering time series')
    t_baryv_start = time.time()

    # Get data directory, basename and filetype to generate glob string of data files to collectively process.
    working_dir = get_value(hotpotato,'working_dir')
    data_dir = get_value(hotpotato,'directory')
    basename = get_value(hotpotato,'basename')
    file_type = get_value(hotpotato,'filetype')
    file_ext = file_extensions[file_type]
    data_glob_string = data_dir+'/'+basename+'*'+file_ext

    os.chdir(data_dir)
    cmd_baryv = 'prepdata -numout 8 -dm 0.0 -o %s_temp -%s %s | grep Average'% (basename, file_type, data_glob_string)
    # TODO: make check_output function in method.py
    baryv = float(sp.check_output(cmd_baryv,shell=True).decode('utf-8').split('=')[1])
    set_value(hotpotato,'baryv',baryv) # Store baryv in hotpotato.
    print('Average barycentric velocity (c) = %s'% (baryv))
    try_cmd('rm %s_temp.*'% (basename))
    os.chdir(working_dir)
    
    # TODO: method.py function
    t_baryv_end = time.time()
    baryv_time = (t_baryv_end - t_baryv_start)
    print('Average barycentric velocity determination took %f seconds.\n' %(baryv_time))

    return hotpotato
