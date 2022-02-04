import requests
import getpass
from datetime import datetime
import json
import csv
import os
import urllib3
urllib3.disable_warnings()

sq_session = requests.Session()

uPass = getpass.getpass(prompt='Password: ', stream=None)
sq_session.auth = requests.auth.HTTPBasicAuth(getpass.getuser(), uPass)
sq_session.verify = 0 

sq_session.headers.update({'XSRF-TOKEN': 'api'})

iq_url = "https://sonarqube.standard.com"

def savecsvreport(file_name, csvrecords):
    if not os.path.exists("output"):
        os.mkdir("output")
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.csv'
    report_data = open(reportfile, 'w', encoding='utf-8', newline='')
    csvwriter = csv.writer(report_data)
    if csvrecords:
        header = csvrecords[0].keys()
        csvwriter.writerow(header)
    for rep_record in csvrecords:
        csvwriter.writerow(rep_record.values())
    report_data.close()

def saveOutput(file_name, d):
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.json'
    fileout = open(reportfile,"w")
    fileout.write(json.dumps(d, indent=4))
    fileout.close

allApps=[]
for i in range(20):
    apps = sq_session.get(f'{iq_url}/sonarqube/api/components/search?qualifiers=TRK&ps=40&p={i+1}').json()["components"]
    allApps = allApps + apps

#print("apps: "+ str(apps))
finalReport = []
for app in allApps:
    #print("app: "+ app["key"])
    measures = {}
    finalReportRecord = {}
    measures = sq_session.get(f'{iq_url}/sonarqube/api/components/app?component={app["key"]}').json()
    print("measures: "+ str(measures))
    measures.update(measures["measures"])
    measures.pop("measures")
    measures.pop("key")
    measures.pop("uuid")
    measures.pop("name")
    measures.pop("longName")
    measures.pop("q")
    measures.pop("fav")
    measures.pop("canMarkAsFavorite")
    measures.setdefault("lines","")
    measures.setdefault("coverage","")
    measures.setdefault("duplicationDensity","")
    measures.setdefault("issues","")
    measures.setdefault("tests","")
    # finalReportRecord["project"] = measures["project"]
    # finalReportRecord["projectName"] = measures["projectName"]
    # finalReportRecord["lines"] = measures["lines"]
    # finalReportRecord["coverage"] = measures["coverage"]
    # finalReportRecord["duplicationDensity"] = measures["duplicationDensity"]
    # finalReportRecord["issues"] = measures["issues"]
    # finalReportRecord["tests"] = measures["tests"]

    #print("measures: "+ str(measures))
    finalReport.append(measures)
savecsvreport("sq_Report", finalReport)
#saveOutput("sq_Report", finalReport)
#saveOutput("sq_Report-measures", measures)