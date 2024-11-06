#!/usr/bin/env python
import json
import os
import re
import shlex
import shutil
from datetime import datetime, timezone
from urllib import request

import pandas as pd

source_dir = "C:\\git\\igsayi\\incapsula-logs-downloader\\script\\process"
os.chdir(source_dir)
directory_list = os.listdir()
patt = re.compile(r"(([\W+])) (.*)")
log_attributes = {
    "sourceServiceName": "site",
    # "siteid": "siteid",
    # "suid": "accountid",
    "deviceFacility": "pop",
    "cs2": "Javascript",
    "cs3": "Cookie",
    "cs1": "Capta",
    "cs4": "VisitorID",
    "dproc": "browser_type",
    "cs6": "Cient_app",
    "ccode": "country",
    "cicode": "city",
    "Customer": "sub-account",
    "start": "start",
    "request": "request",
    "requestMethod": "requestMethod",
    "cn1": "response_code",
    "app": "app",
    "act": "result",
    "sip": "sip",
    "in": "in",
    "xff": "xff",
    "cs10": "rules",
    "cpt": "cport",
    "src": "src",
    "ver": "TLS",
    "end": "end",
    "ref": "ref",
    "qstr": "qstr",
    "postbody": "postbody",
}

sers = []
for datafile in directory_list:
    if not datafile.endswith(".log"):
        continue
    filein = open(datafile, encoding="utf8")

    for line in filein:
        ser = {"FileName": datafile}
        matt = re.findall(patt, line)
        if not matt:
            continue
        time, time, key_values = matt[0]

        for token in shlex.split((key_values.replace("'", "\\'"))):
            try:
                token_key = token.split("=", 1)[0]
                token_key = log_attributes[token_key]
                token_value = token.split("=", 1)[1]
            except:
                continue
            match token_key:
                case "start":
                    token_value = datetime.fromtimestamp(float(token_value) / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                case "end":
                    token_value = datetime.fromtimestamp(float(token_value) / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            ser.update({token_key: token_value})
        sers.append(ser)

df = pd.DataFrame(sers)
df.to_excel(f'output-{format(datetime.now().strftime("%Y%m%d%H%M"))}.xlsx', index=False)
for datafile in directory_list:
    if not datafile.endswith(".log"):
        continue
    shutil.move(datafile, "Done\\" + datafile)
