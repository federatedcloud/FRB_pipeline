import numpy as np
import matplotlib.pyplot as plt


def open_results(filename):
    '''
    Open a clust (results) file, and return a tuple containing three items:
        (1) params -- string containing the parameter values
        (2) stat_names -- list of statistics recorded
        (3) stat_lists -- list of lists where each sublist contains the values
                          of all statistics for a given candidate
    '''
    f= open(filename)
    lines_list= f.readlines()

    params= lines_list[1]
    stat_names= lines_list[3].split()
    stat_lists= lines_list[4:]
    
    N= len(stat_lists)
    for j in range(N):
        stat_lists[j]= list(map(float, stat_lists[j].split()))
    
    # convert stat_lists into an array 
    #stat_lists= np.array(stat_lists)

    return (params, stat_names, stat_lists)


def sort_results(stat_lists, stat_names, sort_stat):
    '''
        Sorts the stat_lists according to the statistic specified by sort_stat.
        Returns: sorted stat_lists
        Parameters:
            stat_lists (list of lists): a list of sublists, each sublist is a line of statistics from
                       a cluster text  file
            stat_names (list): contains the names of statistics, in order
            sort_stat (string): the name of the statistic to sort by

    '''
    sort_index= stat_names.index(sort_stat)
    stat_lists.sort(reverse= True, key=lambda x:x[sort_index])
    return stat_lists


def aggregate_results(rel_path, filelist, sort_stat, block_size, overlap):
    '''
        Combine several "block" results files together to into a single candidates list
        Parameters:
            rel_path (string) -- relative path to files
            filelist (string) -- list of results files
            num_blocks (int)

    '''
    print('rel_path: ' + rel_path)
    print('filelist: ' + str(filelist))
    print('sortstat: ' + sort_stat)
    print('block_size: ' + str(block_size))
    print('overlap: ' + str(overlap))
    
    all_stat_lists= []
    for block in filelist:
        (params, stat_names, stat_lists)= open_results(rel_path + '/' + block)
        n= int(block[5:].split('_')[0])
        print('Block ' + str(n))
        #convert to numpy array to shift
        stat_array= np.array(stat_lists)
        print('stat_array shape: ' + str(stat_array.shape))
        # shift t_min, t_max, v_min, v_max appropriately
        print('First row before shifting: ' + str(stat_array[0,:]))
        stat_array[:,6]+= n * (block_size - overlap)
        stat_array[:,7]+= n * (block_size - overlap)
        print('First row after shifting: ' + str(stat_array[0,:]))

        # convert back to lists for sorting
        shifted_stat_lists= stat_array.tolist()
        for stat_list in shifted_stat_lists:
            all_stat_lists.append(stat_list)

    print('len(all_stat_lists): ' + str(len(all_stat_lists)))
    print('first cand before sorting: ' + str(all_stat_lists[0]))
    all_stat_lists= sort_results(all_stat_lists, stat_names, sort_stat)
    print('first cand after sorting: ' + str(all_stat_lists[0]))

    save(all_stat_lists, params, stat_names, sort_stat, rel_path + '/AggResults_SortedBy_' + sort_stat + '.txt')


def save(stat_lists, params, stat_names, sort_stat, save_name):
    f= open(save_name, mode='w')
    f.write('fof results, with:' + '\n' + params + '\n')
    Nstats= len(stat_names)
    Ncands= len(stat_lists)
    for j in range(Nstats):
        f.write(stat_names[j])
        f.write("\t")
    f.write("\n")
    for j in range(Ncands):
        for k in range(Nstats):
            if k in [0,6,7,8,9]:
                f.write("%d\t" %(stat_lists[j][k]))
            else:
                f.write("%f\t" %(stat_lists[j][k]))
        f.write("\n")


def save_sorted_file(rel_path, txt_filename, params, stat_lists, stat_names, sort_stat):
    '''
    Create a new text file identical to an existing results file, but sorted
    by a given statistic.

    Parameters:
        rel_path (string): path from current directory where the output is saved
        txt_filename (string): name of the (unsorted) results file to sort
        params (string): the FOF parameters used to obtain this results file
        stat_lists (list of lists): each sublist contains the values of all 
                                    recorded statistics for a single candidate
        stat_names (list): Names of the statistics recorded in this results file
        sort_stat (string): Name of statistic by which to sort the candidates

    Outputs:
        "SortedBy" + sort_stat + "_" + txt_filename: a new results text file,
            where the candidates have been sorted by <sort_stat>
    '''

    f= open(rel_path + "SortedBy" + sort_stat + "_" + txt_filename, mode="w")
    f.write("fof results, with:" + "\n" + params + "\n")
    Nstats= len(stat_names)
    Ncands= len(stat_lists)
    for j in range(Nstats):
        f.write(stat_names[j])
        f.write("\t")
    f.write("\n")
    for j in range(Ncands):
        for k in range(Nstats):
            if k in [0,6,7,8,9]:
                f.write("%d\t" %(stat_lists[j][k]))
            else:
                f.write("%f\t" %(stat_lists[j][k]))
        f.write("\n")


def print_vertical_statline(statline, stat_names):
    for j in range(len(statline)):
        print(stat_names[j] + "= " + str(statline[j]))

    print("\n\n")


def specific_plot(ar, tstart, tend, vstart, vend):
    # tstart, tend, vstart, vend are INDICES
    plt.imshow(ar[vstart:vend, tstart:tend])
    plt.savefig("fig_t_{0}_to_{1}_v_{2}_to_{3}.png".format(int(tstart), int(tend), int(vstart), int(vend)))
    plt.show()


def plot_clusters(npy_filename, txt_filename, sort_stat, n):
    

    # Get the statistics, and sort
    (params, stat_names, stat_lists)= open_results(txt_filename)
    if n <= len(stat_lists):
        sorted_stat_lists= sort_results(stat_lists, stat_names, sort_stat)[0:n]
    else:
        sorted_stat_lists= sort_results(stat_lists, stat_names, sort_stat)

    # Get location of starting and end times and frequencies
    t_min_index= stat_names.index("t_min")
    t_max_index= stat_names.index("t_max")
    v_min_index= stat_names.index("v_min")
    v_max_index= stat_names.index("v_max")

    # Plot
    ar= np.load(npy_filename)
    ar= ar[ar.files[0]]
    for j in range(n):
        statline= sorted_stat_lists[j]
        #print_vertical_statline(statline, stat_names)
        print(int(statline[6]), int(statline[7]), int(statline[8]), int(statline[9]))
        #specific_plot(ar, int(statline[t_min_index]), int(statline[t_max_index]), int(statline[v_min_index]), int(statline[v_max_index]))
