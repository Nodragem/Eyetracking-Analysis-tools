__author__ = 'c1248317'

__author__ = 'c1248317'

import pandas as pd
import numpy as np
import re, ntpath

def parseEventsFromEyelinkASC(path):
    """
    output format:
        time TRIAL_ID Fixation Fixation_ECC Fixation_DIR Target Target_ECC  Target_DIR END_TRIAL
28  7438593        1       ON         30.0         15.0    NaN        NaN       NaN       NaN
29  7438605        1  PRESSED         30.0         15.0    NaN        NaN       NaN       NaN
30  7438626        1      OFF         30.0         15.0    NaN        NaN       NaN       NaN
31  7438645        1      NaN          NaN          NaN     ON       12.0       8.0       NaN
32  7438690        1      NaN          NaN          NaN    OFF       12.0       8.0       NaN
36  7441536        1      NaN          NaN          NaN    NaN        NaN       NaN      TRUE

    """
    current_line = 0
    toSkip = []
    event_table = pd.DataFrame()
    info = []
    trial_id = 0
    trial_type = 0
    isTrialPlaying = False
    index = 0
    with open(path) as f:
        for line in f:
            if not re.match("\d+", line):
                toSkip.append(current_line)
                if "TRIAL REPEATED after Calibration" in line:
                    if "TRIAL_ID" in event_table.columns:
                        #print trial_id
                        event_table = event_table.ix[event_table.TRIAL_ID != trial_id, :]
                elif "STIMULUS" in line:
                    ## if STIMULUS found in line, expected format: STIMULUS NAME STATE ECCENTRICITY DIRECTION
                    words = line.split()
                    origin = words.index("STIMULUS")
                    event_table.loc[index, "time"] = int(re.findall("\d+", line)[0])
                    event_table.loc[index, "TRIAL_ID"] = trial_id
                    event_table.loc[index, "TRIAL_TYPE"] = trial_type
                    event_table.loc[index, "TRIAL_CODE"] = trial_code
                    event_table.loc[index, words[origin+1]] = words[origin+2] ##  ON OFF PRESSED
                    event_table.loc[index, words[origin+1]+"_ECC"] = words[origin+3] ##  ECCENTRICITY
                    event_table.loc[index, words[origin+1]+"_DIR"] = words[origin+4] ## DIRECTION
                elif "END" in line:
                    ## The marker END indicate the END of a trial
                    if not isTrialPlaying:
                        print "Error: a marker END has been found without a previous TRIALID pair."
                    isTrialPlaying = False
                    event_table.loc[index, "time"] = int(re.findall("\d+", line)[0])
                    event_table.loc[index, "END_TRIAL"] = "TRUE"
                    event_table.loc[index, "TRIAL_ID"] = trial_id
                    event_table.loc[index, "TRIAL_TYPE"] = trial_type
                    event_table.loc[index, "TRIAL_CODE"] = trial_code
                elif "TRIALID" in line:
                    words = line.split()
                    ## increment the trialid if TRIALID found in line
                    if isTrialPlaying:
                        print "Error: a marker TRIALID has been found without a previous END pair."
                    isTrialPlaying = True
                    trial_id += 1
                    origin = words.index("TRIAL_TYPE")
                    trial_type = words[origin + 1]
                    trial_code = words[origin + 3]
                index += 1
            current_line += 1

        if (len(np.unique(event_table["TRIAL_ID"])) != np.sum(event_table.END_TRIAL == "TRUE")):
            print "One of the trial has been cut before END."
            print "Nb trial ID: ", len(np.unique(event_table["TRIAL_ID"]))
            print "Nb trial end:", np.sum(event_table.END_TRIAL == "TRUE")
            event_table = event_table.ix[event_table.TRIAL_ID != trial_id, :]
            print "To correct it, the last trial has been removed."

        return toSkip, current_line, event_table

# s1, s2, s3 = parseEventsFromEyelinkASC("ACS1gpB2.asc")
# print "Please wait..."
# print s3.head(10)
#print s1
#        time TRIAL_ID TRIAL_TYPE TRIAL_CODE Fixation Fixation_ECC Fixation_DIR  \
# 28  3729176        1        0.0      212.0       ON        6.750      -90.000
# 37  3730347        1        0.0      212.0  PRESSED        6.750      -90.000
# 38  3730864        1        0.0      212.0      OFF        6.750      -90.000
# 39  3731243        1        0.0      212.0      NaN          NaN          NaN
# 47  3731681        1        0.0      212.0      NaN          NaN          NaN
# 65  3731912        2        0.0      112.0       ON        6.750      -90.000
# 74  3732738        2        0.0      112.0  PRESSED        6.750      -90.000
# 75  3733610        2        0.0      112.0      OFF        6.750      -90.000
# 76  3733699        2        0.0      112.0      NaN          NaN          NaN
# 84  3734138        2        0.0      112.0      NaN          NaN          NaN
#
#      S1 S1_ECC  S1_DIR END_TRIAL   S2 S2_ECC S2_DIR
# 28  NaN    NaN     NaN       NaN  NaN    NaN    NaN
# 37  NaN    NaN     NaN       NaN  NaN    NaN    NaN
# 38  NaN    NaN     NaN       NaN  NaN    NaN    NaN
# 39   ON  6.750  90.000       NaN  NaN    NaN    NaN
# 47  NaN    NaN     NaN      TRUE  NaN    NaN    NaN
# 65  NaN    NaN     NaN       NaN  NaN    NaN    NaN
# 74  NaN    NaN     NaN       NaN  NaN    NaN    NaN
# 75  NaN    NaN     NaN       NaN  NaN    NaN    NaN
# 76   ON  6.750  90.000       NaN  NaN    NaN    NaN
# 84  NaN    NaN     NaN      TRUE  NaN    NaN    NaN

def populateDataWithTrialEvents(trial_event, table_data):
    start_trial = trial_event.time.values[0]
    end_trial = trial_event.time.values[-1]
    print "\rTrial ID: ", trial_event.TRIAL_ID.values[0],
    # copy the slice of the data table corresponding to the current trial:
    trial_data = table_data.loc[(table_data.time >= start_trial) & (table_data.time <= end_trial), :].copy(deep=True)
    # Then we iterate through the columns:
    for col_names in trial_event:
        if "_ECC" in col_names:
            ## extract the non null values
            events = trial_event.loc[pd.notnull(trial_event[col_names])] ## no column selection
            if len(events) > 0: ## if there are non-null values, take the first value (the other values are normally the same than the first)
                trial_data[col_names] = float(events[col_names].values[0])
                #trial_data[col_names] = trial_data[col_names].astype(float)
        elif "_DIR" in col_names: ## same than in "_ECC" condition
            events = trial_event.loc[pd.notnull(trial_event[col_names])]
            if len(events) > 0:
                trial_data[col_names] = float(events[col_names].values[0])
                #trial_data[col_names] = trial_data[col_names].astype(float)
        elif col_names in ["TRIAL_TYPE", "TRIAL_CODE"]:
            events = trial_event.loc[pd.notnull(trial_event[col_names])]
            if len(events) > 0:
                trial_data[col_names] = float(events[col_names].values[0])
        elif col_names not in ["time", "TRIAL_ID", "END_TRIAL", "TRIAL_TYPE", "TRIAL_CODE"]: ## if the column is a Stimulus State, then:
            # We don't copy "time" it is already in the data table, "TRIAL ID" will be added automatically. And END_TRIAL is not usefull.
            trial_data[col_names] = "OFF"
            events = trial_event.loc[pd.notnull(trial_event[col_names])]
            if isinstance(events, pd.DataFrame): ## if there is several lines for which the tested colunms is not null
                for i, line in events.iterrows():
                    trial_data.ix[trial_data.time >= line.time, col_names] = line[col_names]
            elif isinstance(events, pd.Series): ## if there is only one line which is not null for the tested column
                trial_data.ix[trial_data.time >= events.time, col_names] = events[col_names]


    if len(trial_data["time"]) > 0:    #print col_names
        trial_data["time"] -= trial_data["time"].values[0]
    trial_data.reset_index(drop=True, inplace=True)
    return trial_data

def populateDataWithEvents(table_event, table_data):
    grouped = table_event.groupby("TRIAL_ID")
    #print grouped.groups
    full_data = grouped.apply(populateDataWithTrialEvents, table_data) ## apply call twice the function
    full_data.reset_index(level=0, inplace=True)
    #print "\n", full_data.head(10)
    #import sys
    #sys.exit(0)
    return full_data

def addEyelinkASCtoHDF5(path1, path_to_store): ## we store everything in one big file.
    name = ntpath.basename(path1).split(".")[0]
    ## we check each lines, extract info,
    ## and we keep in memory which line in not a eye movement's table_data:
    print "Processing of %s started:"%name
    print "Extract info..."
    toSkip, total_lines, table_event = parseEventsFromEyelinkASC(path1)
    print "Lines to skip: %.2f percent."%(len(toSkip)/total_lines)
    #print table_event
    ## see the function checkLines to understand the column names:
    ## the value return by the Eye Tracker are in this order:
    col_names2 = ['time', 'xp', 'yp', 'ps', 'vx', 'vy']
    table_data = pd.read_table(path1,
                  names = col_names2,
                  na_values = [".", "..."],
                  usecols=[0,1,2,3,4,5],
                  skiprows = toSkip, skipinitialspace=True)
    #We merge the information from checkLines with the eye movement's table_data:
    print "Merging of Info and Records..."
    big_table = populateDataWithEvents(table_event, table_data)
    # let's print a sample to check:
    # print big_table.head(10)
    # print big_table.dtypes
    print "Save %s in %s ..."%(name, path_to_store)
    # big_table.to_csv("mockoutput2.csv")
    store = pd.HDFStore(path_to_store)
    store[name] = big_table
    store.close()
    print "Saved!"


#addEyelinkASCtoHDF5("ACS1gpB2.asc", "blabla")