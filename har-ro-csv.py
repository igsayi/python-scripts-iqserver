#!/usr/bin/env python
import json

import pandas as pd

datafile = "output/portalacc.standard.com.har"
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

    for har_header in har_entry["response"]["headers"]:
        if har_header["name"].upper() in interested_headers:
            report_record[har_header["name"].upper()] = har_header["value"]
    final_report.append(report_record)

df = pd.DataFrame(final_report)
df.to_csv("output/portalacc.standard.com.har.csv", index=False)
