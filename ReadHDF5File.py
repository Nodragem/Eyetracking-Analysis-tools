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
size = os.path.getsize(raw_store)
print raw_store, "file size is:", str(size/(1024*1024)), "Mb"
istore = pd.HDFStore(raw_store)
print istore

answer = raw_input("Do you want to [O]pen a dataframe or to [D]elete a dataframe or to [M]erge dataframe? \n")

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

elif answer == "D":
    while answer != "Q":
        while answer not in istore.keys() and answer != "Q":
            answer = raw_input("Enter name ([Q] to quit): ")
        if answer != "Q":
            istore.remove(answer)
            print "%s successfully removed!"%answer
            answer = ""

# elif answer == "M":
#     while answer != "Q":
#         while answer not in istore.keys() and answer != "Q":
#             answer = raw_input("Enter merging factor ([Q] to quit): ")
#         if answer != "Q":
#             all_names = fm.selectName(answer,"!", istore)
#             for key in all_names
#             B1["Block"] = 1
#             B2["Block"] = 2
#             new_data = B1.append(B2, ignore_index = True)
#             print "%s successfully removed!"%answer
#             answer = ""



istore.close()
print "finie!"


