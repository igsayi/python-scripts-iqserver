import math
import json
import requests
import os
import csv
from datetime import datetime
#---------------------------------
iq_session = requests.Session()

authstring = "user:password"
baseurl = "https://iqserver.standard.com"
reportingstage = "release"

creds = authstring.split(":")
iq_session.auth = requests.auth.HTTPBasicAuth(creds[0], creds[1] )
iq_session.verify = 'hlblbclmp001-standard-com-chain.pem'
if not os.path.exists("output"):
        os.mkdir("output")

# Organizations
def getOrgs():
        url = '{}/api/v2/organizations'.format(baseurl)
        print("Org url " + str(url))
        orgresponse = iq_session.get(url).json()
        #print("reponse " + str(orgresponse))
        return orgresponse["organizations"]

# Applications
def getApps(orgs):
        appId = []
        appdetail = {}
        appsdetails= []
        url = '{}/api/v2/applications'.format(baseurl)
        print("App url " + str(url))
        appresponse = iq_session.get(url).json()
        #print("reponse " + str(appresponse))
        for app in appresponse["applications"]:
                orgname = ""
                repdataurl = ""
                appDistributed=""
                appHosted=""
                appInternal=""
                appRemediated=""
                #print("App Tag is after if " + apptag["tagId"])
                for org in orgs:
                        if app["organizationId"] == org["id"]:
                                orgname = org["name"]
                        if org["id"]=="ROOT_ORGANIZATION_ID":
                                for tag in org["tags"]:
                                        for apptag in app["applicationTags"]:
                                                if tag["id"] == apptag["tagId"]:
                                                        if tag["name"] == "Distributed":
                                                                appDistributed = "Distributed"
                                                        if tag["name"] == "Hosted":
                                                                appHosted = "Hosted"
                                                        if tag["name"] == "Internal":
                                                                appInternal = "Internal"
                                                        if tag["name"] == "Remediated":
                                                                appRemediated = "Remediated"
                if appRemediated=="Remediated" or appRemediated=="":  #we can App Categories here 
                        url2 = '{}/api/v2/reports/applications/{}'.format(baseurl,app["id"])
                        #print("App report url " + str(url2))
                        apprepresponse = iq_session.get(url2).json()
                        #print("appreport response "+ str(apprepresponse))
                        for rep in apprepresponse:
                                #print(str(rep))
                                if rep["stage"]==reportingstage:
                                        repdataurl = rep["reportDataUrl"]
                        appId.append(app["id"])
                        appdetail["appId"]=app["id"]
                        appdetail["appname"]=app["name"]
                        appdetail["orgname"] = orgname
                        appdetail["redatapurl"] = repdataurl
                        appdetail["appDistributed"] = appDistributed
                        appdetail["appHosted"] = appHosted
                        appdetail["appInternal"] = appInternal
                        appdetail["appRemediated"] = appRemediated
                        #print("each appdetail " + str(appdetail))
                        appsdetails.append(dict(appdetail))
                        #print("cumilative appdetail" + str(appsdetails))
        #print("Final appsetails: " + str(appsdetails))
        return appsdetails

orgs = getOrgs()
#print("Orgs are"+ str(orgs))
appDets = getApps(orgs)
#print("Apps List")

custReportrecord = {}
customReport= []

for apprep in appDets:
        #print("release stage" + " -" +rep["applicationId"] +" - " + rep["reportDataUrl"])
        if "api" in apprep["redatapurl"]:
                print(apprep["appname"] +" - " + apprep["redatapurl"])
                url = '{}/{}'.format(baseurl,apprep["redatapurl"])
                print("report url" + " - " +url)
                response1 = iq_session.get(url).json()
                for comp in response1["components"]:
                        if comp["securityData"] is not None and len(comp["securityData"]) >0:
                                secIssues=comp["securityData"]["securityIssues"]
                                if secIssues is not None and len(secIssues) > 0:
                                        packageUrl = comp["packageUrl"]
                                        compFormat = comp["componentIdentifier"]["format"] #To take care of Non-Maven components
                                        coordinates = comp["componentIdentifier"]["coordinates"] #comp["packageUrl"]
                                        coordinates1 = {} #To take care of Non-Maven components
                                        if compFormat=="gem" or compFormat=="a-name":
                                                coordinates1["artifactId"]=coordinates["name"]
                                        if compFormat=="nuget":
                                                coordinates1["artifactId"]=coordinates["packageId"]
                                        coordinates1["extension"]=""
                                        coordinates1["groupId"]=""
                                        coordinates1["version"]=coordinates["version"]
                                        
                                        for secIssue in secIssues:
                                                #print(str(comp["securityData"]["securityIssues"]))
                                                custReportrecord = apprep.copy()
                                                custReportrecord.pop("appId")
                                                #custReportrecord.pop("apptagId")
                                                custReportrecord.pop("redatapurl")
                                                #custReportrecord["packageUrl"]=packageUrl
                                                custReportrecord["CVE"]=secIssue["reference"]
                                                custReportrecord["severity"]=math.trunc(secIssue["severity"])
                                                custReportrecord["status"]=secIssue["status"]
                                                custReportrecord["compFormat"]=compFormat
                                                
                                                if "classifier" in coordinates:
                                                        custReportrecord.update(dict(coordinates))
                                                        custReportrecord.pop("classifier")
                                                else:
                                                        custReportrecord.update(dict(coordinates1)) #To take care of Non-Maven components
                                                #custReportrecord["url"]=secIssue["url"]
                                                #print("CustReprecord: "+ str(custReportrecord))
                                                customReport.append(dict(custReportrecord))
finalCustomReport = {"customreport": customReport}
finalreport_data = finalCustomReport["customreport"]
#print("Custom Report: " + str((finalreport_data)))

reportfile = 'output/CVE-Report-{}-{}.csv'.format(reportingstage,datetime.now().strftime("%Y%m%d"))
report_data = open(reportfile, 'w', newline='')
csvwriter = csv.writer(report_data)

header = finalreport_data[0].keys()
csvwriter.writerow(header)
for rep_record in finalreport_data:
        csvwriter.writerow(rep_record.values())
report_data.close()




