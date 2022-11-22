import json
import os
import sys

import pandas as pd

os.chdir("c:/Temp/work/RASP-POC/20221121")
directory_list = os.listdir()
rasplogsList = []
for datafile in directory_list:
    if not datafile.endswith(".json"):
        continue
    filein = open(datafile, encoding="utf8")
    print("Started Reading JSON file which contains multiple JSON document")
    for jsonObj in filein:
        try:
            rasplogDict = json.loads(jsonObj)
        except:
            print("Oops!", sys.exc_info()[0], "occurred.")
            rasplogDict = {"vendor": "Imperva"}
        finally:
            rasplogDict.update({"File": datafile})
            rasplogsList.append(rasplogDict)
    filein.close
print("Printing each JSON Decoded Object")
df = pd.DataFrame.from_dict(rasplogsList)
df.to_excel("rasp-json.xlsx")
