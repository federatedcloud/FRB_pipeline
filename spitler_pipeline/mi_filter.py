
# Contains a single function, "mi_filter1", which reviews candidate pulses
# bases on their modulation indices. The user can choose to keep either:
# (1) a set number of the best candidates, or 
# (2) all candidates with modulation index above a certain threshold

# Relevant Parameters in "params.py": 
#   mi_mode -- "threshold" or "quantity" 
#   mi_quantity -- number of candidates to keep
#   mi_threshold -- modulation index threshold 
   
def mi_filter1(work_dir, basename, mi_mode, flex_val):
    
    # Arguments:
    #   work_dir -- directory that contains the ".mi" file with modulation index data for candidates
    #   mi_mode -- see above
    #   basename --  see "params.py"
    #   flex_val -- either "mi_quantity" or "mi_threshold", depending on the "mi_mode" selected
    
    if mi_mode != "threshold" and mi_mode != "quantity":
        print "mi_mode parameter is set incorrectly. Quitting..."
        return
    
    infile = work_dir + "/%s_MF.mi" %(basename,)
    outfile = work_dir + "/%s_MF_fin.mi" %(basename,)
    f = open(infile, 'r') # open in reading mode
    fout = open(outfile, 'w') # new blank file for writing

    initial_cand_list = f.readlines()
    j = 0
    indexed_list = []
    new_cands = []
 
    if mi_mode == "threshold":
        
        mi_threshold = flex_val

        num_cands = 0
        for line in initial_cand_list:
            print line.split() 
            mi = float(line.split()[7])
            if mi < mi_threshold:
                new_cands.append(line)      
                indexed_list.append([mi,j])
                num_cands += 1
                #fout.write(line)
            j += 1
        
        #indexed_list.sort(key= lambda x: x[0])
        #for pair in indexed_list:
        #    new_cands.append(pair[0])
        #    fout.write(initial_cand_list[pair[1]])
        new_cands.sort(key = lambda x: float(x[(len(x)-9):(len(x)-1)]))    
        
        print "Outfile format is:\nDM    SNR      Time(s)     Sample      Downfact    Ibar    Ibar2   MI\n"
        for line in new_cands:
            fout.write(line)

        print "Number of candidates with modulation index below mi_threshold is: " + str(num_cands)
        return new_cands

    if mi_mode == "quantity":
        mi_quantity = flex_val

        index_list = [] # list of indices for <mi_quantity> best mod. indices

        for line in initial_cand_list:
            l = len(line)
            mi = float(line[(l-9):(l-1)])
            indexed_list.append([mi,j])
            j += 1

        # sort the candidates by modulation index (lowest to highest)
        indexed_list.sort(key= lambda x: x[0])

        # choose the <mi_quantity> candidates with the lowest modulation indices
        cut_indexed_list = indexed_list[0:mi_quantity]
        
        # get a list of the lines we want to initial candidates file
        for pair in cut_indexed_list:
            index_list.append(pair[1])

        # write new candidates info to output file
        print "Outfile format is:\n DM   SNR   Time(s)   Sample   Downfact   Ibar   Ibar2   MI"
        for i in index_list:
            cand = initial_cand_list[i]
            fout.write(cand)
            new_cands.append(cand)

        return new_cands    

    # close in/out files        
    f.close()
    fout.close()
