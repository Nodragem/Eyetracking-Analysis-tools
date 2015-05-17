__author__ = 'c1248317'

import os, sys
import eyetools.filemanager as fm
import pandas as pd
import numpy as np
from pprint import pprint

current_path = sys.path[0]
#raw_path = "D:\Users\Administrator\Dropbox\Document\experiments\Data_Double_Stim"

from Tkinter import *
from tkFileDialog import *
import subprocess
root = Tk()
root.wm_title("Read HDF5")

vim_path = "D:/GVimPortable/GVimPortable.exe"
fileName = askopenfilename(parent=root)

raw_store = fileName

answer = ""

while answer != "Q":
    size = os.path.getsize(raw_store)
    istore = pd.HDFStore(raw_store)
    print raw_store, "file size is:", str(size/(1024*1024)), "Mb"
    print istore, "--------\n"
    answer = raw_input("""Do you want to:
     [O]pen a dataframe,
     [D]elete a dataframe,
     [M]erge dataframes?
     [Q] to quit \n""")

    if answer == "O":
        while answer != "Q":
            matches = []
            while len(matches)<1 and answer != "Q":
                answer = raw_input("Enter name ([Q] to quit): ")
                matches = fm.selectName(answer, "!", istore)
            if answer != "Q":
                print "First match found: %s"%matches[0]
                df = istore[matches[0]]
                df.to_csv("./tmp2.data", sep = "\t")
                subprocess.call([vim_path, "./tmp2.data"], shell=True)
                os.remove("./tmp2.data")
                answer = ""
        answer = ""

    elif answer == "D":
        while answer != "Q":
            while answer not in istore.keys() and answer != "Q":
                print "Choose a name in the list of Dataframes."
                answer = raw_input("Enter name ([Q] to quit): ")
            if answer != "Q":
                istore.remove(answer)
                print "%s successfully removed!"%answer
                answer = "D"
        answer = ""

    elif answer == "M":
        while answer != "Q":
            while answer not in istore.keys() and answer != "Q":
                answer = raw_input("Enter merging factor ([Q] to quit): ")
            if answer != "Q":
                list_df, all_names = fm.getDataFrame(answer,"!", istore)
                B1 = list_df[0]
                B1["Block"] = 1
                for i, key in enumerate(all_names[1:]):
                    list_df[i]["Block"] = i+1
                    B1 = B1.append(list_df[i], ignore_index = True)
                istore[answer+"merged"] = B1
                print "%s successfully Merged!"%answer
                answer = ""
        answer = ""
    elif answer == "RC":
        istore.close()
        cmd = ["ptrepack", "--chunkshape=auto", "--propindexes", "--complevel=9", "--complib=blosc", fileName, fileName+"comp"]
        error = subprocess.check_call(cmd, shell=False)
        #os.system('ptrepack --chunkshape=auto --propindexes --complevel=9 --complib=blosc "%s" "%s"'%(fileName, fileName))
        print error
    istore.close()





istore.close()
print "finie!"
