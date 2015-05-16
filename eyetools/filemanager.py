__author__ = 'c1248317'

import pandas as pd
import numpy as np
import re, ntpath

def checkLines(path):
    current_line = 0
    toSkip = []
    times = [[],[],[],[],[]]
    info = []
    with open(path) as f:
        for line in f:
            if not re.match("\d+", line):
                toSkip.append(current_line)
                if "TRIAL REPEATED after Calibration" in line:
                    del info[-1]
                    del times[4][-1]
                elif "Fixation ON" in line:
                    times[0].append(int(re.findall("\d+", line)[0]))
                elif "Fixation PRESSED" in line: ## stimulus 1 ON
                    times[1].append(int(re.findall("\d+", line)[0]))
                elif "Fixation OFF" in line: ## stimulus 1 ON
                    times[2].append(int(re.findall("\d+", line)[0]))
                    times[3].append(-1)
                elif "STIMULUS 1/2 OFF/ON" in line: # stimulus 2 ON (stim 1 OFF)
                    #times[3].append(int(re.findall("\d+", line)[0]))
                    times[3][-1] = int(re.findall("\d+", line)[0])
                elif "END" in line: ## Stimulus 2 OFF
                    times[4].append(int(re.findall("\d+", line)[0]))
                elif "TRIALID" in line:
                    t =  map(float, line.split("[")[1].split() )[0:4]# barbarian way
                    t[0] += 1 ## start from 1
                    info.append(t)
            current_line += 1
        print "Check lines equallity: ",len(times[0]),"-", len(info), "=", (len(times[0]) - len(info))
        if ((len(times[0]) - len(info)) == -1): ## the last trial got cutted while running
            ## we remove this trial, which has only a TRIAL ID and END tag
            print "remove the last line"
            del info[-1]
            del times[4][-1] ## time[1] contains the END tag
        print "time col length:", len(times[0]),len(times[1]),len(times[2]),len(times[3]), "info length:", len(info)
        print np.array(times).shape, np.array(info, dtype=float).shape

        return toSkip, current_line, np.hstack((np.array(times).T, np.array(info, dtype=float)))

def mergeInfoAndRecord(info, record):
    datamat = np.zeros((record.shape[0],11))
    datamat[:, 0:6] = record.values
    ## a copy is much more performance friendly:
    time_col = datamat[:,0].copy()
    ## there are the columns featuring times, and which need to be offset by the start time:
    #col_to_offset = np.array((0, 6, 7))
    end = [0]
    start = 0
    #tick = time.time()
    print "Matrix creation"
    ## time, xp, yp, ps, vx, vy, trial ID, type, target ecc, target dir, stimuliON
    for index, p in enumerate(info.values): ## read index trial find in the EDF file.
        ## p = [ "fixation ON","PRESSED", "stimuli 1 ON", "stimuli 2 ON","trial OFF","trial ID", "trial type","targer ecc", "target dir"]
        print "\r trial ID:", index, #, p[4:],
        start = end[0] ## we start the search from the end of the previous
        end = np.where( time_col == (p[4]-1))[0] ## we end the search at the end of the current trial
        #print "start-end-p[0]:", time_col[start], time_col[end], p[0]
        ## don't be tricked by the [0]: the first element of np.where() is a list:
        datamat_select = np.where( time_col[start:end] >= p[0] )[0] + start
        if len(datamat_select) < 1:
            print "there is a trial where the fixation cross didn't appear."
            print "You MUST remove it to have a good Dataframe."
        sd = datamat[datamat_select]
        #print datamat_select
        ## ! this is wrong: what's wrong?
        sd[:,6:10] = np.repeat([p[5:]], len(datamat_select), axis=0) ## p[5] is after the time information
        sd_select = np.where( time_col[datamat_select] >= p[1] )[0]
        #print sd_select, p[:]
        sd[sd_select, -1] = 1 ## put a marker 1 if the time is after fixation PRESSED (button pressed by the participant)
        sd_select = np.where( time_col[datamat_select] >= p[2] )[0]
        sd[sd_select, -1] = 2 ## put a marker 2 if the time is after STIMLUS 1 ON
        if p[3] > 0:
            sd_select = np.where( time_col[datamat_select] >= p[3] )[0]
            if (len(sd_select)>0): ## put a marker 3 if the time is after STIMLUS 2 ON
                    sd[sd_select, -1] = 3
        sd[:,0] -= p[0] ## fixation_ON is the time zero (col_to_offset was used here)
        datamat[datamat_select] = sd

    #tock = time.time() - tick
    #print "Done in %.4f second"%tock
    return datamat

def extractAndStoreFromASCII(path1, path_to_store): ## we store everything in one big file.
    name = ntpath.basename(path1).split(".")[0]
    ## we check each lines, extract info,
    ## and we keep in memory which line in not a eye movement's record:
    print "Processing of %s started:"%name
    print "Extract info..."
    toSkip, total_lines, record = checkLines(path1)
    print "Lines to skip: %.2f percent."%(len(toSkip)/total_lines)
    ## see the function checkLines to understand the column names:
    col_names1 = [ "fixation ON","PRESSED", "stimuli 1 ON", "stimuli 2 ON","trial OFF","trial ID",
                 "trial type","targer ecc", "target dir"]
    info = pd.DataFrame(record, columns = col_names1)
    print "Extract Records..."
    ## the value return by the Eye Tracker are in this order:
    col_names2 = ['time', 'xp', 'yp', 'ps', 'vx', 'vy' ]
    record = pd.read_table(path1,
                  names = col_names2,
                  na_values = [".", "..."],
                  usecols=[0,1,2,3,4,5],
                  skiprows = toSkip, skipinitialspace=True)
    #We merge the information from checkLines with the eye movement's record:
    print "Merging of Info and Records..."
    big_table = mergeInfoAndRecord(info, record)
    col_names3 = ['time', 'xp', 'yp', 'ps', 'vx', 'vy', "trial ID",
                 "trial type","targer ecc", "target dir", "stimuliON"]
    tab = pd.DataFrame(big_table, columns = col_names3 )
    # let's print a sample to check:
    print "Save %s in %s ..."%(name, path_to_store)
    store = pd.HDFStore(path_to_store)
    store[name] = tab
    store.close()
    print "Saved!"

def getDataFrame(expression, to_avoid, istore, suffixe = ""):
    all_names = selectName(expression,to_avoid, istore, suffixe="")
    list_dataframes = []
    for name in all_names:
        B1 = istore[name]
        list_dataframes.append(B1)
    return list_dataframes, all_names

def getDataFramesFromList(list_dfname, store):
    l_df = []
    for name in list_dfname:
        l_df.append(store.select(name))
    return l_df

def selectName(expression, to_avoid, istore, suffixe = ""):
    file_selector = [e+suffixe for e in expression]
    to_avoid = to_avoid
    storekeys = istore.keys()
    list_names = [key[1:] for key in storekeys  if any(string in key for string in file_selector)] ## e[1:] to remove the / in front of the name
    list_names = [e for e in list_names if to_avoid not in e]
    print "List of selected files: "
    print list_names
    return list_names

def mergeBlocks(expression, istore, nameB1 = "B1", nameB2 = "B2", suffixe="-seq", to_avoid = ""):
    all_names = selectName(expression,to_avoid, istore)
    list_dataframes = []
    list_names = []
    listB1 = [e for e in all_names if nameB1 in e]
    listB2 = [e for e in all_names if nameB2 in e]
    for nB1 in listB1:
        B1 = istore[nB1]
        #B1 = B1.groupby("trial_ID").apply(removeRT)
        expectedname = nB1.split("B1")[0] + "B2" + suffixe
        if expectedname in listB2:
            nB2 = expectedname
        else:
            print "Block 2 not found for ", nB1
            continue
        list_names.append(nB1.split("B1")[0])
        B2 = istore[nB2]
        #B2 = B2.groupby("trial_ID").apply(removeRT)
        B1["Block"] = 1
        B2["Block"] = 2
        new_data = B1.append(B2, ignore_index = True)
        list_dataframes.append(new_data)
    return list_dataframes, list_names

def mergePartitions(istore, expected_nb_trial = 1600, path_log="./"):
    """
    Fusion parted Sessions, resetting the indexes.
    NOTE 1: by running this program, the EDF2Panda program will not recognise the merge files as already converted (the
     EDF and the Dataframe names won't match anymore).
    NOTE 2: the name of the first part of a parted dataframe has to finish with "-part1".
    The same notation has to be used for the following parts.

    """
    import time
    if isinstance(istore, str):
        istore = pd.HDFStore(istore)

    def printO(s, f):
        print s
        f.write(s+"\n")

    ## ---------- START ------------
    with open(path_log+"merging_log.log", "a") as f:
        localtime   = time.localtime()
        timeString  = time.strftime("the %d-%m-%Y at %H:%M:%S \n", localtime)
        f.write("\n########################### \n \n-Log from "+timeString)
        f.write("\n\n")
        list_df = istore.keys()
        duplicate = [e for e in list_df if "part" in e]
        if len(duplicate) < 2:
            printO("No duplicates found!", f)
        else:
            printO("Found parted dataframe: \n"+str(duplicate), f)
            names_dataframe = list(set([e.split("-")[0] for e in duplicate]))
            printO("Will be merged in: \n"+ str(names_dataframe), f)
            list_newdf = []
            for name in names_dataframe:
                printO("\n *----------------------\n", f)
                list_to_merged = [e for e in duplicate if name in e]
                printO(str(name) + " will contain " + str(list_to_merged),f)
                dfs_to_merged = getDataFramesFromList(list_to_merged, istore)
                new_df = pd.concat(dfs_to_merged, ignore_index=True)
                list_newdf.append(new_df)
                #print new_df[new_df["trial ID"] != 0]
                trials_done = new_df["trial ID"].ix[new_df.time==0].values.tolist()
                #trials_done = np.unique(new_df["trial ID"]).tolist()
                printO("Nb of trials: "+str(len(trials_done)),f)
                printO("Trials missing: ",f)
                printO(str([e for e in range(1, expected_nb_trial + 1) if e not in trials_done]), f)
                printO("Trials recorded twice: ", f)
                printO(str(set([e for e in trials_done if trials_done.count(e) > 1])), f)

    if len(duplicate)>=2:
        print "new df:", names_dataframe
        print "old df:", duplicate
        a = raw_input("Replace the old dataframes with the new one? (Y/n) >> ")
        if a == "Y":
            for name, df in zip(names_dataframe, list_newdf):
                istore[name[1:]]= df
            for name in duplicate:
                istore.remove(name)
            print "Saved!"
        else:
            print "Not saved."
    istore.close()


def resolveDuplicatedTrialID(istore, df_name):
    """
    For duplicate trials in a dataframe.
    Here a program to check if there is duplicate trials and to unduplicate them:
    """

    df = istore[df_name]
    recorded_trials = df["trial ID"].ix[df.time==0].values.tolist()
    dupli = list(set([e for e in recorded_trials if recorded_trials.count(e) > 1]))
    print "Duplicates: ", dupli
    print "Nb Duplicates: ", len(dupli)
    print "Nb recorded trials:", len(recorded_trials)
    last_ID = recorded_trials[-1] + 1
    print "Next available ID:", last_ID

    ## you may have to run this code several times if you have more than 1 duplicate for some trials:
    if len(dupli)> 0:
        for i, trial_no in enumerate(dupli):
            s1 = df[df['trial ID']==trial_no]
            start = s1[s1["time"]==0].index[1] ## take the index of the second occurence of time==0
            end = s1.index[-1] ## take the index of the last row tagged with this trial ID
            print "Will rename trial ID from %d to %d with the following ID: %d"%(start, end, last_ID + i)
            df.ix[start:end, "trial ID"] = last_ID + i

    answer = raw_input("Do you want to replace the DataFrame? (Y/n) >> ")
    if answer == "Y":
        istore[df_name] = df
        istore.close()
        print "Saved!"


def getGraphOfMissingValues(reg_expression, istore, to_avoid = ""):
    import matplotlib.pyplot as plt
    perc_NA_list = []
    perc_aNA_list = []
    key_list =  istore.keys()
    print "In the Folder:", key_list
    key_list = [name for name in istore.keys() if re.match(reg_expression, name)]
    print "Selected files for the graph, ", key_list

    for key in key_list:
        df = istore.select(key)
        df = df[df["trial ID"] != 0]
        print "file opened: ", key
        print "statistic summary:"
        nb_trials = len(np.unique(df.loc[:,"trial ID"]))
        print "nb trials:", nb_trials
        perc_NA = 100*np.sum(np.isnan(df.loc[:,"xp"])) / float(df.shape[0])
        perc_NA_list.append(perc_NA)
        print "percentage of NA:", perc_NA
        perc_aNA = 100*np.sum(np.isnan(df.loc[df["stimuliON"]>0,"xp"])) / float(df.loc[df["stimuliON"]>0,"xp"].shape[0])
        perc_aNA_list.append(perc_aNA)
        print "percentage of NA after the stimuli onset:", perc_aNA

        print "available clean trials:"
        select = (np.isnan(df.loc[:,"xp"]))
        trials_clean = nb_trials - len(np.unique(df.ix[select, "trial ID"]))
        print trials_clean
        print "percentage of clean trials:", trials_clean/float(nb_trials)

    width = 0.35
    plt.figure()
    plt.bar(np.arange(len(key_list)), perc_NA_list, width = width, color = 'red')
    plt.bar(np.arange(len(key_list))+width, perc_aNA_list, width = width, color = 'blue')
    plt.ylim(0, 100)
    plt.xticks(np.arange(len(key_list)), key_list, rotation = 45)
    plt.title("Percentage of Missing Data Per File")
    plt.xlabel("Files")
    plt.legend(["Over the trials","Over trials but after target ONSET"])
    plt.show()

def getRejectionPercentagePerSubject(list_subjects, istore):
    #list_subjects = ["AN", "BD", "KM","GM","RI"]
    rej_persubject =[]
    for subject in list_subjects:
        list_dataframes, list_conditions = mergeBlocks(subject, istore)
        istore.close()
        i=0
        rej_percondition = []
        for tab, cond in zip(list_dataframes, list_conditions):
            if "rejected" in tab.columns:
                rej = np.sum(tab.rejected == True)/float(len(tab.rejected))
                rej_percondition.append(rej)
            else:
                print cond, "is not clean! ..."
                continue
        rej_persubject.append(rej_percondition)

    rej_persubject = np.array(rej_persubject)
    print "Rejection percentage: "
    for tab, name in zip(rej_persubject, list_subjects):
        print name , " : " , tab.mean()*100 , "%%"