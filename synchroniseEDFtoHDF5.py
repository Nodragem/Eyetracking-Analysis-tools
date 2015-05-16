import time
import pandas as pd
import ntpath, os, glob, sys
from eyetools import filemanager as fm
from eyetools import EDFparser as eparser
import subprocess

tick = time.time()

with open("currentpath.ph", "rb") as f: ## thta's a file in the same folder describing the out_path and input_path
    file_path = f.readlines()

path_edf = file_path[0].rstrip() ## first line should head to the EDF folder
path_asc = file_path[1].rstrip() ## second line should head to the ASC folder
os.chdir(path_edf)
print "EDF folder:\n\t - %s"%path_edf
print "ASC folder:\n\t - %s"%path_asc

path_to_store = file_path[2].rstrip()
print "HDF5 folder \n\t - %s"%path_to_store ## third line should head to the HDF5 folder

if not os.path.exists(path_asc):
    os.makedirs(path_asc)
if not os.path.exists(os.path.dirname(path_to_store) ):
    os.makedirs(os.path.dirname(path_to_store) )

list_ascnames = []
list_edfnotconverted = []
list_ascfiles = glob.glob(path_asc+"*.asc")
list_edffiles = glob.glob(path_edf+"[!x]*.EDF") ## file marked with a x at the start of the filename won't be taken

for asc in list_ascfiles:
    list_ascnames.append(ntpath.basename(asc).split(".")[0])

for edf in list_edffiles:
    pbase = ntpath.basename(edf).split(".")[0]
    if pbase not in list_ascnames:
        list_edfnotconverted.append(edf)

print "\nList to synchronised between EDF and ASC files: ",
print "\n\t - "+"\n\t - ".join(ntpath.basename(e) for e in list_edfnotconverted)
if len(list_edfnotconverted) > 0 and "y" == raw_input("Is it OK to synchronized the above files? (y/N)"):
    total_file = len(list_edfnotconverted)
    for i, fname in enumerate(list_edfnotconverted):
        print "\nSynchronising '%s': [%d/%d]"%(os.path.basename(fname), i+1, total_file)
        print fname
        print path_asc
        #cmd = ["edf2asc", fname, "-t", "-sg", "-vel", "-ftime", "-p", path_asc]
        os.system('edf2asc "%s" -t -sg -vel -ftime -p "%s"'%(fname, path_asc[:-1]))
        #error = subprocess.check_call(cmd, shell=False)
        #print error
    print "All synchronized!"
else:
    print "No EDF/ASC files synchronization has been made."

list_names = []
list_ascfiles = glob.glob(path_asc+"*.asc")
for p in list_ascfiles:
    list_names.append(ntpath.basename(p).split(".")[0])

store = pd.HDFStore(path_to_store, complevel=9, complib='blosc')
already_saved = [s.split('/')[1] for s in store.keys()]

if len(sys.argv) > 1:
    if sys.argv[1] == "-f" and len(sys.argv)>2:
        files_to_read = [sys.argv[2]] ## one file
    elif sys.argv[1] == "-a":
        files_to_read = list_names ##  read all files in the folder
    elif sys.argv[1] == "-u":
        files_to_read = [i for i in list_names if i not in already_saved ] ## read only the one not already saved
else:
    print "No update of the HDF5... "
    exit(0)

print "Number of ASC files to add to the HDF5: %d"%len(files_to_read)
print files_to_read

answer = raw_input("Please confirm by pressing Enter or kill the program...")

tick_all = time.time()
for name in files_to_read:
    path_to_file = path_asc+name+".asc"
    tick = time.time()
    #fm.extractAndStoreFromASCII(path_to_file, path_to_store)
    eparser.addEyelinkASCtoHDF5(path_to_file, path_to_store)
    tock = time.time() - tick
    print "Time to Process and Save: %.2f seconds"%tock
tock_all = time.time() - tick_all
print "All files have been treated and stored!"
print "Store file: %s"%path_to_store

print "Time used: %d min %d s"%(int(tock_all/60), int(tock_all%60))

print "Check for Partitioned Files..."
fm.mergePartitions(path_to_store, 800)

