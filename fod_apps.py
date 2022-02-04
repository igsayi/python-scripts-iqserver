import requests
import getpass
from datetime import datetime
import json
import csv
import os

import urllib
import sys

base_url = 'https://api.ams.fortify.com'
client_id='9a3c3bd0-cfa3-49a6-9c18-c1b3d4c20457'
client_secret='QTAsSkdBcUdqUFFHSmZod2lNSWpRMCpkKDZFOXQ50'
tokenfile = f'output/token.json'

def savecsvreport(file_name, csvrecords):
    if not os.path.exists("output"):
        os.mkdir("output")
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.csv'
    report_data = open(reportfile, 'w', newline='')
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

def GetToken():
    # GetToken is the method used to authenticate to the FoD API, and extract the bearer token from the response
    
    print("In GetToken")
    authorizationPayload = "scope=api-tenant&grant_type=client_credentials&client_id=" + client_id + "&client_secret=" + client_secret
    headers = {'content-type': "application/x-www-form-urlencoded", 'cache-control': "no-cache"}
    response = requests.post(base_url+'/oauth/token', data=authorizationPayload, headers=headers)
    responseObject = json.loads(response.text)
    bearer = responseObject.get("access_token", "no token")
    print(response.text)
    if bearer != "no token":
        print("New Token generated")
        fileout = open(tokenfile, "w")
        fileout.write(json.dumps(responseObject, indent=4))
        return responseObject['access_token']
    else:
        print(response.text)
    return None


def GetVulnReport():

    fileout = open(tokenfile, "r")
    bearerToken = json.loads(fileout.read())["access_token"]
    headers = {'Accept' : 'application/json', 'Authorization' : "Bearer " + bearerToken}
    responseObject = requests.get(base_url+'/api/v3/releases', headers=headers).json()
    #print("responseObject: "+ str(responseObject))
    rels = responseObject.get("items", "no items")
    if rels == "no items":
        if responseObject["responseCode"] == "401":
            print("calling GetToken..")
            bearerToken = GetToken()
            print("bear token is: "+bearerToken)
            headers = {'Accept' : 'application/json', 'Authorization' : "Bearer " + bearerToken}
            responseObject = requests.get(base_url+'/api/v3/releases', headers=headers).json()
            print("with new token: "+str(responseObject["totalCount"]))
            rels = responseObject.get("items", "no items")
    else:
        print("print with old token: "+str(responseObject["totalCount"]))

    vulnReport=[]

    for relId in rels:
        if relId["issueCount"] > 0:
            vulns = requests.get(base_url+'/api/v3/releases/'+str(relId["releaseId"])+'/vulnerabilities?includeFixed=true&includeSuppressed=true', headers=headers).json()["items"]
            for vulnId in vulns:
                vulnReportRow = {}

                vulnReportRow["applicationName"]=relId["applicationName"]
                vulnReportRow["releaseName"]=relId["releaseName"]
                vulnReportRow["releaseId"]=relId["releaseId"]
                vulnReportRow["id"]=vulnId["id"]
                vulnReportRow["severityString"]=vulnId["severityString"]
                vulnReportRow["severity"]=vulnId["severity"]
                vulnReportRow["category"]=vulnId["category"]
                vulnReportRow["kingdom"]=vulnId["kingdom"]
                vulnReportRow["package"]=vulnId["package"]
                vulnReportRow["primaryLocation"]=vulnId["primaryLocation"]
                vulnReportRow["assignedUser"]=vulnId["assignedUser"]
                vulnReportRow["isSuppressed"]=vulnId["isSuppressed"]
                vulnReportRow["auditorStatus"]=vulnId["auditorStatus"]
                vulnReportRow["closedDate"]=vulnId["closedDate"]
                vulnReportRow["closedStatus"]=vulnId["closedStatus"]
                vulnReportRow["developerStatus"]=vulnId["developerStatus"]
                vulnReportRow["introducedDate"]=vulnId["introducedDate"]
                vulnReportRow["status"]=vulnId["status"]
                vulnReportRow["timeToFixDays"]=vulnId["timeToFixDays"]
                print(vulnId["vulnId"])
                #print(requests.get(base_url+'/api/v3/releases/'+str(relId["releaseId"])+'/vulnerabilities/'+str(vulnId["vulnId"])+'/recommendations', headers=headers))
                #vulnReportRow["summary"]=requests.get(base_url+'/api/v3/releases/'+str(relId["releaseId"])+'/vulnerabilities/'+str(vulnId["vulnId"])+'/details', headers=headers).json()["summary"]
                #vulnReportRow["notes"]=requests.get(base_url+'/api/v3/releases/'+str(relId["releaseId"])+'/vulnerabilities/'+str(vulnId["vulnId"])+'/summary', headers=headers).json()["notes"]
                #vulnReportRow["recommendations"]=requests.get(base_url+'/api/v3/releases/'+str(relId["releaseId"])+'/vulnerabilities/'+str(vulnId["vulnId"])+'/recommendations', headers=headers).json()["recommendations"]
                allData=requests.get(base_url+'/api/v3/releases/'+str(relId["releaseId"])+'/vulnerabilities/'+str(vulnId["vulnId"])+'/all-data', headers=headers).json()

                vulnReport.append(vulnReportRow)
    vulnReport = sorted(sorted(vulnReport, key = lambda i: i["severity"], reverse=True), key = lambda i: i["applicationName"])

    savecsvreport("vulnReport", vulnReport)
    #saveOutput("vulnReport", vulnReport)

GetVulnReport()






