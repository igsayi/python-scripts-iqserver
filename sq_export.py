import csv
import getpass
import html
import json
import os
from datetime import datetime

import urllib3
from requests import Session
from requests.auth import HTTPBasicAuth


def savecsvreport(file_name, csvrecords):
    if not os.path.exists("output"):
        os.mkdir("output")
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.csv'
    report_data = open(reportfile, "w", encoding="utf-8", newline="")
    csvwriter = csv.writer(report_data)
    if csvrecords:
        header = csvrecords[0].keys()
        csvwriter.writerow(header)
    for rep_record in csvrecords:
        csvwriter.writerow(rep_record.values())
    report_data.close()


def saveOutput(file_name, d):
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.json'
    fileout = open(reportfile, "w")
    fileout.write(json.dumps(d, indent=4))
    fileout.close


def main():

    urllib3.disable_warnings()

    sq_session = Session()
    sq_session.auth = HTTPBasicAuth(getpass.getuser(), getpass.getpass(prompt="Password: ", stream=None))
    sq_session.verify = False
    sq_session.headers.update({"XSRF-TOKEN": "api"})

    sq_url = "https://sonarqube.standard.com"

    branchName = html.escape(input("Branch Name (default is master): "))
    if len(branchName) > 0:
        print("Pulling metrics for branch: " + str(branchName))
        branchName = "branch=" + str(branchName) + "&"
    else:
        print("Pulling metrics for default branch master")

    compName = html.escape(input("application name: "))
    #    compName = "eb-gac-ggf-group-summary-api"
    if len(compName) > 0:
        print("Searching for: " + str(compName))
    else:
        print("Running the Report for all applications")

    allApps = []
    for i in range(2):
        if len(compName) > 0:
            apps = sq_session.get(f"{sq_url}/sonarqube/api/components/search?qualifiers=TRK&ps=400&p={i+1}&q={compName}").json()[
                "components"
            ]
        else:
            apps = sq_session.get(f"{sq_url}/sonarqube/api/components/search?qualifiers=TRK&ps=400&p={i+1}").json()["components"]
        allApps = allApps + apps

    # print("apps: "+ str(apps))
    finalReport = []
    for app in allApps:
        print("app: " + app["key"])
        measures = {}
        finalReportRecord = {}
        # measures = sq_session.get(f'{sq_url}/sonarqube/api/components/app?{branchName}component={app["key"]}').json()
        response = measures = sq_session.get(f'{sq_url}/sonarqube/api/components/app?{branchName}component={app["key"]}')
        if response.status_code != 200:
            continue
        measures = response.json()
        componentShow = sq_session.get(f'{sq_url}/sonarqube/api/components/show?{branchName}component={app["key"]}').json()["component"]
        # print("measures: "+ str(measures))
        # print("componentShow: "+ str(componentShow))
        measures.update(measures["measures"])
        measures.update(componentShow)
        measures.pop("measures")
        measures.pop("key")
        measures.pop("uuid")
        measures.pop("name")
        measures.pop("longName")
        measures.pop("q")
        measures.pop("fav")
        measures.pop("canMarkAsFavorite")
        measures.setdefault("lines", "")
        measures.setdefault("coverage", "")
        measures.setdefault("duplicationDensity", "")
        measures.setdefault("issues", "")
        measures.setdefault("tests", "")
        measures.setdefault("analysisDate", "")
        measures.setdefault("version", "")
        finalReportRecord["project"] = measures["project"]
        finalReportRecord["projectName"] = measures["projectName"]
        finalReportRecord["lines"] = measures["lines"]
        finalReportRecord["coverage"] = measures["coverage"]
        finalReportRecord["duplicationDensity"] = measures["duplicationDensity"]
        finalReportRecord["issues"] = measures["issues"]
        finalReportRecord["tests"] = measures["tests"]
        finalReportRecord["analysisDate"] = measures["analysisDate"]
        finalReportRecord["version"] = measures["version"]

        # print("measures: "+ str(measures))
        # finalReport.append(measures)
        finalReport.append(finalReportRecord)
    savecsvreport("sq_Report-" + compName, finalReport)
    # saveOutput("sq_Report", finalReport)
    # saveOutput("sq_Report-measures", measures)


if __name__ == "__main__":
    main()
