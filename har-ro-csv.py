#!/usr/bin/env python
import json
import os

import pandas as pd

# datafile = "output/portalacc.standard.com.har"

os.chdir("C:\Temp\Downloads\har")
directory_list = os.listdir()
for datafile in directory_list:
    if not datafile.endswith(".har"):
        continue
    filein = open(datafile, encoding="utf8")
    har_json = json.load(filein)
    filein.close

    interested_headers = {
        "ACCESS-CONTROL-ALLOW-ORIGIN",
        "CACHE-CONTROL",
        "CLEAR-SITE-DATA",
        "CONTENT-DISPOSITION",
        "CONTENT-SECURITY-POLICY",
        "CONTENT-TYPE",
        "CROSS-ORIGIN-EMBEDDER-POLICY",
        "CROSS-ORIGIN-OPENER-POLICY",
        "CROSS-ORIGIN-RESOURCE-POLICY",
        "EXPECT-CT",
        "PERMISSIONS-POLICY",
        "REFERRER-POLICY",
        "STRICT-TRANSPORT-SECURITY",
        "X-CONTENT-TYPE-OPTIONS",
        "X-FRAME-OPTIONS",
        "X-XSS-PROTECTION",
        "EXPIRES",
        "PRAGMA",
        "SET-COOKIE",
    }

    final_report = []
    for har_entry in har_json["log"]["entries"]:
        report_record = {}

        report_record["url_name"] = har_entry["request"]["url"]
        report_record["resource_type"] = har_entry["_resourceType"]
        report_record["priority"] = har_entry["_priority"]
        if "connection" in har_entry:
            report_record["connection"] = har_entry["connection"]
        else:
            report_record["connection"] = ""
        report_record["serverIPAddress"] = har_entry["serverIPAddress"]

        for har_header in har_entry["response"]["headers"]:
            if har_header["name"].upper() in interested_headers:
                if har_header["name"].upper() in report_record:
                    report_record[har_header["name"].upper()] = report_record[har_header["name"].upper()] + "\n" + har_header["value"]
                else:
                    report_record[har_header["name"].upper()] = har_header["value"]
        final_report.append(report_record)

    df = pd.DataFrame(final_report)
    df.to_excel((f"{datafile}.xlsx"), index=False)
