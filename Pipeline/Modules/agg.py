import numpy as np
import matplotlib.pyplot as plt
import os

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


def open_all_blocks(loc, filelist, fof_params):
    '''
    Parameter:
        fof_params= tuple of the 7 FOF parameters
        filelist= a list of names of files to aggregate into one
        loc= directory containing the files in the filelist 
    Returns:
        a list containing the statlines from every file in the filelist
    '''

    grand_list= []
    N= len(filelist)
    for k in range(N):
        filename= loc + "/" + filelist[k]
        if os.path.exists(filename):
            params, stat_names, stat_lists= open_results(filename)
            if params == fof_params:
                grand_list.append(stat_lists)
                print(filename + " will be aggregated.")
            else:
                print(filename + " does not have the requested fof parameters")
        else:
            print("The requested file -- " + filename + " -- does not exist.")
    
    return grand_list


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


def truncate_results(stat_lists, n, high=True):
    return stat_lists[0:n] if high else stat_lists[(-1)*n:]


def write_file(loc, fof_params, stat_lists, stat_names, sort_stat):
    
    (m1, m2, tsamp, vsamp, t_gap, v_gap)= fof_params
    filename = "agg_clust_%.1f_%d_%d_%d_%d_%d.txt" %(m1, m2, tsamp, vsamp, t_gap, v_gap)
    f = open(loc + "/" + filename, "w")
    f.write("Aggregated (all blocks) fof results, with\nm1=%.2f   m2=%.2f   tsamp=%.2f   vsamp=%.2f   t_gap=%.2f   v_gap=%.2f\n\n" \
            %(m1,m2,tsamp,vsamp,t_gap,v_gap))
    f.write("N \tclust_SNR\t\tsig_mean\tsig_max\t\tSNR_mean\tSNR_max\t\tt_min\t\tt_max\t\t\tv_min\t\tv_max\t\tslope\tDM\n")
    
    N= len(stat_lists):
    for k in range(N):
        lk= stat_lists[k]
        f.write("%d\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\n" \
                  %(lk[0], lk[1], lk[2], lk[3], lk[4], lk[5], lk[6], 
                    lk[7], lk[8], lk[9], lk[10], lk[11]))


def print_vertical_statline(statline, stat_names):
    for j in range(len(statline)):
        print(stat_names[j] + "= " + str(statline[j]))

    print("\n\n")


