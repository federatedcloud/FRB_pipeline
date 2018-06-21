



def get_plot_times(work_dir, basename, tread):

    # Get a list of the time intervals to make plots of
    # "tread" is the width (in time) of plots

    times_list = []
    infile = work_dir + "%s_MF_fin.mi" %(basename,)
    f = open(infile, 'r')
    cand_list = f.readlines()
    # add all time values to times_list
    for line in cand_list:
        line_split = line.split()
        times_list.append([float(line_split[2]),float(line_split[0])])
    # times_list.sort()
    
    plot_times = []
    for [time,dm] in times_list:
        T = time - (tread/2.0)
        T_new = True
        # check if T is already in an interval that will be plotted (T_new flag)    
        for [ts,dms] in plot_times:
            if time > ts and time < (ts+tread):
                T_new = False
        if T_new:
            plot_times.append([T,dm])

    return plot_times

