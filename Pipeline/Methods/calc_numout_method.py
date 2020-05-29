from method import *

# Map file types to their corresponding extensions.
file_extensions = {'psrfits':'.fits','filterbank':'.fil'}

def main(hotpotato):

    print('\nCalculating suitable FFT length')
    t_FFTlength_start = time.time()

    # Get data directory, basename and filetype to generate glob string of data files to collectively process.
    working_dir = get_value(hotpotato,'working_dir')
    data_dir = get_value(hotpotato,'directory')
    basename = get_value(hotpotato,'basename')
    file_type = get_value(hotpotato,'filetype')
    file_ext = file_extensions[file_type]
    data_glob_string = data_dir+'/'+basename+'*'+file_ext

    # Generate file list.
    file_list = sorted(glob(data_glob_string))
    N_files = len(file_list) # Number of files.

    # Calculate total number of time samples across all input files.
    # First (N-1) files usually contain equal number of time samples. The final file may alone differ in the number of time samples.
    # Calculate no. of time samples in the first file.
    N = 0
    os.chdir(data_dir)
    for i in range(N_files):
        readfile_cmd = 'rm -rf %s_readfile_temp.out; readfile %s > %s_readfile_temp.out'% (basename, file_list[i], basename)
        try_cmd(readfile_cmd,stdout=sp.DEVNULL)
        infile = open(basename + '_readfile_temp.out','r')
        for line in infile:
            line = line.strip('\n').strip(' ')
            print(line)
            if line.startswith('Spectra per file'):
                line = line.split('=')
                N += int(float(line[1]))
        infile.close()
    try_cmd('rm %s_readfile_temp.out'% (basename))
    os.chdir(working_dir)
    print('Total no. of time samples across files = %d'% (N))

    # Find integer "numout" > N that is suitable for fast FFTs with fftw.
    choose_numout_cmd = 'chooseN.py %d'% (N)
    # TODO: check_output in method.py
    numout = int(sp.check_output(choose_numout_cmd,shell=True))
    print('Suitable value of numout = %d'% (numout))
    set_value(hotpotato, 'numout', numout) # Store numout value in hotpotato.
    
    # TODO: turn this into a method.py function
    t_FFTlength_end = time.time()
    FFTlength_time = (t_FFTlength_end - t_FFTlength_start)
    print('FFT length determination took %f seconds.\n' %(FFTlength_time))

    return hotpotato
