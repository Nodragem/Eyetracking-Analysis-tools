current_path = "D:\Google Drive\Work\Experiences\EyeTracking"
import os
import pandas as pd
import eyetools.multicleaning as cl
import ntpath, glob

cl.printHello()
## ------- PARAMETERS ----------
## write "" for all of them, write the complete file's name to select it only,
## write the initial of the subject's name to select all files of a subject:
file_selector = [""]
to_avoid = "!" ## put "!" to not avoid anything (we assumed there is no ! in your file name)
COMPUTE_TABLE_ONLY = False ## will just compute the markers and suspected trial, without plot
forced = True ## force the computation of markers and suspected trials
TRIAL_COL_NAME = "TRIAL_ID"
#TRIAL_COL_NAME = "trial ID

## ------ INITIALIZATION --------
with open("currentpath.ph", "rb") as f: ## thta's a file in the same folder describing the out_path and input_path
    file_path = f.readlines()

path_output = file_path[4].rstrip()
output_store = file_path[3].rstrip()
input_store = file_path[2].rstrip()
print "Suspected trials and ouput folder:\n\t - %s"%path_output
print "The input HDF5 for trajectories of all trials will be:\n\t - %s"%input_store
print "The output HDF5 file marking end and start of saccades will be: \n\t - %s"%output_store ## third line should head to the HDF5 folder

if not os.path.exists(path_output):
    os.makedirs(path_output)
istore = pd.HDFStore(input_store)
os.chdir(current_path)
ostore = pd.HDFStore(output_store)

list_names = [key[1:] for key in istore.keys() if any(string in key for string in file_selector)] ## e[1:] to remove the / in front of the name
list_names = [e for e in list_names if to_avoid not in e]
print "Start cleaning for suject %s:"%file_selector
print "DataFrame:"
print list_names



if COMPUTE_TABLE_ONLY:
    ## ------- PROGRAM COMPUTE ONLY -----------
    pr = cl.ProgressBar("Files Analysed: ", value_max= len(list_names), pos=(0, 0))
    for file_name in list_names:
        print "\n\n #################\n Will open and clean %s:"%file_name
        df = istore.select(file_name)
        #df.reset_index(level=0, inplace=True) ## we may want to put it in the writing method
        df = df[df[TRIAL_COL_NAME] != 0]
        #df = df[df[TRIAL_COL_NAME] < 10]
        markers_tab = cl.createAMarkersTable(df, file_name, output_store, cl.computeMarkers, force_rewritting=forced) ## can close the ostore
        suspect_tab = cl.createSuspectTrialsList(df, markers_tab, savename=path_output+file_name, force_rewritting=forced)
        pr.step(1)
    print "All done!"
else:
    ## ------ PROGRAM COMPUTE and DISPLAY ONE by ONE -----------
    answer = ""
    current = 0
    file_name = ""
    while answer != "stop":
        #istore = pd.HDFStore(input_store)
        if not ostore.is_open:
            ostore = pd.HDFStore(output_store)

        list_already_checked = [k.split("/")[1] for k in ostore.keys() if "rejected" in ostore[k].columns]
        list_already_checked = [e.split("-")[0] for e in list_already_checked]
        #print list_already_checked
        to_display = list(list_names)
        list_already_cleaned = [ntpath.basename(e) for e in glob.glob(path_output+"*.csv")]
        list_already_cleaned = [e.split("-")[0] for e in list_already_cleaned]
        to_display = [e+"[c]" if e in list_already_cleaned else e for e in to_display]
        to_display = [e+"[u]" if e.split("[c]")[0] in list_already_checked else e for e in to_display]
        to_display[current % len(list_names)] += "*"
        print "\n\nCurrently selected file marked with *, [c] indicates that the file as been analysed for saccades, [u] indicates it has been checked by the experimenter:"
        for index, e in enumerate(to_display):
            print str(index), "-", e, "\n" if index%4 == 3 else "\t",
        print "Current File: ", file_name
        answer = raw_input("Enter your next action: "
                        "\n0-9: enter the index of the dataframe to pen"
                           "\np: previous dataframe, "
                           "\nn: next dataframe, "
                           "\ns: same dataframe, "
                           "\n stop: exit the program \n\n >-> ")
        try:
            current = int(answer)
            print "Integer written"
        except ValueError:
            if answer == "p":
                current -= 1
            elif answer == "n":
                current += 1
            elif answer == "stop":
                print "Au revoir..."

        if answer != "stop":
            file_name = list_names[current % len(list_names)]
            print "Will open:", file_name
            df = istore.select(file_name)
            #df.reset_index(level=0, inplace=True)
            print df.head(10)
            df = df[df[TRIAL_COL_NAME] != 0]
            #df = df[df[TRIAL_COL_NAME] < 100]
            markers_tab = cl.createAMarkersTable(df, file_name, output_store, cl.computeMarkers, force_rewritting=forced) ## can close the ostore
            #markers_tab = ostore[file_name+"-seq"]
            #print markers_tab
            suspect_tab = cl.createSuspectTrialsList(df, markers_tab, savename=path_output+file_name, force_rewritting=forced)
            plotter = cl.TrialPlotter(df, file_name, markers_table = markers_tab)
            plotter.detected_trials = suspect_tab
            plotter.setOutput(output_store) ## to enable saving
            plotter.startPlot() ## also can close the ostore
        ostore.close()
        print "Ostore is still opened? ", ostore.is_open
print "Close the HDFStores..."
istore.close()
ostore.close()
print "End!"