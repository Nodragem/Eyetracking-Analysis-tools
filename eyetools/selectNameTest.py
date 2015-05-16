
file_selector = ["AN", "RI", "GM", "BD", "KM"]
#file_selector = ["AN", "RI", "B1"] # "or" relationship

storekeys = ['ANF2TdB1-seq', 'ANF2TdB2-seq', 'ANF2TsB1-seq', 'ANF2TsB2-seq', 'ANF8TdB1-seq', 'ANF8TdB2-seq', 'ANF8TsB1-seq', 'ANF8TsB2-seq', 'BDF2TdB1-seq', 'BDF2TdB2-seq', 'BDF2TsB1-seq', 'BDF2TsB2-seq', 'BDF8TdB1-seq', 'BDF8TdB2-seq', 'BDF8TsB1-seq', 'BDF8TsB2-seq', 'GMF2TdB1-seq', 'GMF2TdB2-seq', 'GMF2TsB1-seq', 'GMF2TsB2-seq', 'GMF8TdB1-seq', 'GMF8TdB2-seq', 'GMF8TsB1-seq', 'GMF8TsB2-seq', 'KMF2TdB1-seq', 'KMF2TdB2-seq', 'KMF2TsB1-seq', 'KMF2TsB2-seq', 'KMF8TdB1-seq', 'KMF8TdB2-seq', 'KMF8TsB1-seq', 'KMF8TsB2-seq', 'RIF2TdB1-seq', 'RIF2TdB2-seq', 'RIF2TsB1-seq', 'RIF2TsB2-seq', 'RIF8TdB1-seq', 'RIF8TdB2-seq', 'RIF8TsB1-seq', 'RIF8TsB2-seq']

#list_names = [key for key in storekeys  if any(string in key for string in file_selector)]

list_names = [key for key in storekeys  if any(string in key for string in file_selector)]

print list_names