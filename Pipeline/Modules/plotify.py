import numpy as np
import matplotlib.pyplot as plt


def open_results(filename):

    f= open(filename)
    lines_list= f.readlines()

    params= lines_list[1]
    stat_names= lines_list[3].split()
    stat_lists= lines_list[4:]
    
    N= len(stat_lists)
    for j in range(N):
        stat_lists[j]= list(map(float, stat_lists[j].split()))

    return (params, stat_names, stat_lists)


def sort_results(stat_lists, stat_names, sort_stat):
    '''
        Sorts the stat_lists according to the statistic specified by sort_stat.
        Returns: sorted stat_lists
        Parameters:
            stat_lists: a list of sublists, each sublist is a line of statistics from
                       a cluster text  file
            stat_names: a list containing the names of statistics, in order
            sort_stat: the name of the statistic to sort by

    '''
    sort_index= stat_names.index(sort_stat)
    stat_lists.sort(reverse= True, key=lambda x:x[sort_index])
    return stat_lists

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

    # Plot
    ar= np.load(npy_filename)
    ar= ar[ar.files[0]]
    for j in range(n):
        statline= sorted_stat_lists[j]
        print_vertical_statline(statline, stat_names)
        print(int(statline[6]), int(statline[7]), int(statline[8]), int(statline[9]))
        specific_plot(ar, int(statline[6]), int(statline[7]), int(statline[8]), int(statline[9]))
