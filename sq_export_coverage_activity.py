import requests
import getpass
from datetime import datetime
import json
import csv
import os
import urllib3
urllib3.disable_warnings()

sq_session = requests.Session()
#uPass = ''
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
for i in range(2):
    apps = sq_session.get(f'{iq_url}/sonarqube/api/components/search?qualifiers=TRK&ps=400&p={i+1}').json()["components"]
    allApps = allApps + apps

#print("apps: "+ str(apps))
finalReport = []
for app in allApps:
    #print("app: "+ app["key"])
    finalReportRecord = {}
    measures = sq_session.get(f'{iq_url}/sonarqube/api/measures/search_history?component={app["key"]}&metrics=coverage&ps=1000').json()["measures"][0]["history"]
    #print("measures: "+ str(measures))
    #print("App: " + app["key"])
    for measure in measures:
        measure.setdefault("value", None)
        finalReportRecord["App"] = app["key"]
        finalReportRecord["date"] = measure["date"]
        finalReportRecord["value"] = measure["value"]
        #print("finalReportRecord: "+ str(measures))
        finalReport.append(finalReportRecord)    

    
    #finalReport.append(measures)
savecsvreport("sq_coverage_activity", finalReport)