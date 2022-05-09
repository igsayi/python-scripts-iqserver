#!/usr/bin/env python
import math
import requests
import getpass
from datetime import datetime
import json
import csv
import os
import pandas as pd
import sys

iq_session = requests.Session()
#uPass = ''
uPass = getpass.getpass(prompt='Password: ', stream=None)
iq_session.auth = requests.auth.HTTPBasicAuth(getpass.getuser(), uPass)
iq_session.verify = 'hlblbclmp001-standard-com-chain.pem'
iq_session.cookies.set('CLM-CSRF-TOKEN', 'api')
iq_session.headers.update({'X-CSRF-TOKEN': 'api'})

iq_url = "https://iqserver.standard.com"

orgsl = iq_session.get(f'{iq_url}/api/v2/organizations').json()["organizations"]
orgs = {}
for org in orgsl:
    orgs.update({org["id"]: org["name"]})

orgtagslist = iq_session.get(f'{iq_url}/api/v2/organizations/ROOT_ORGANIZATION_ID').json()["tags"]
for otl in orgtagslist:
    if otl["name"] == "Internal":
        internalTag = otl["id"]
    if otl["name"] == "Distributed":
        distributedTag = otl["id"]
    if otl["name"] == "Existing Systems":
        ExistingSystemTag = otl["id"]
    if otl["name"] == "New Systems":
        NewSystemTag = otl["id"]

# apps = iq_session.get(f'{iq_url}/api/v2/applications?publicId=AdminEASE').json()["applications"]
apps = iq_session.get(f'{iq_url}/api/v2/applications').json()["applications"]

# Enrich Apps
for app in apps:
    app["organization"] = orgs.get(app["organizationId"])
    app["app_internal"] = ""
    app["app_Distributed"] = ""
    app["app_ExistingSystem"] = ""
    app["app_NewSystem"] = ""    
    
    for apptag in app["applicationTags"]:
        if apptag["tagId"] == internalTag:
            app["app_internal"] = "Inernal"
            app["appExposure"] = "Internal"
        if apptag["tagId"] == distributedTag:
           app["app_Distributed"] = "Distributed"
           app["appExposure"] = "External"
        if apptag["tagId"] == ExistingSystemTag:
           app["app_ExistingSystem"] = "ExistingSystem"
        if apptag["tagId"] == NewSystemTag:
           app["app_NewSystem"] = "NewSystem"                      
    #app.pop("organizationId")
    app.pop("contactUserName")
    #app.pop("applicationTags")
    #app.pop("id")    

def savecsvreport(csvrecords):
    if not os.path.exists("output"):
        os.mkdir("output")
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.csv'
    report_data = open(reportfile, 'w', encoding='utf-8', newline='')
    csvwriter = csv.writer(report_data)
    if csvrecords:
        header = csvrecords[0].keys()
        csvwriter.writerow(header)
    for rep_record in csvrecords:
        csvwriter.writerow(rep_record.values())
    report_data.close()

##################

polviolationreport = []

pols = iq_session.get(f'{iq_url}/api/v2/policies').json()["policies"]

for pol in pols:
    if pol["policyType"] != "security":
        continue
 
    #if pol["threatLevel"] < 6:
    #    continue

    pol_id = pol["id"]
    polViolations = iq_session.get(f'{iq_url}/api/v2/policyViolations?p={pol_id}').json()
    appViolations = polViolations["applicationViolations"]

    for appViolation in appViolations:
        appVApp = appViolation["application"]
        
    #    if orgs.get(appVApp["organizationId"]) == "Alerts and Notifications":
    #        continue
        
        appExposure = "External"
        for app in apps:
            if app["id"] == appVApp["id"] and app["app_internal"] == "Inernal":
                appExposure = "Inernal"

    #    if appExposure == "Inernal":
    #        continue

        unsortedpolViolations = appViolation["policyViolations"] 
        
        sortedPolViolations = sorted(unsortedpolViolations, key = lambda i: (i['openTime'], i['component']["hash"])) 
        prevOpenTime = ""
        prevPackage = ""
        for polViol in sortedPolViolations:
            if polViol["stageId"] != "release":
                continue

            for polcond in polViol["constraintViolations"][0]["reasons"]:
                conReason = polcond["reason"]
                i = conReason.find("with")
                CVEid = conReason[28:i].strip()

            # if prevOpenTime == polViol["openTime"] and prevPackage == polViol["component"]["packageUrl"]:
            #     #policyViolation["CVE"] = policyViolation["CVE"] + "; " + CVEid
            #     CVEid = CVEid + "; " + CVEid
            #     continue

            policyViolation = {}
            
            policyViolation["threatLevel"] = polViol["threatLevel"]
            policyViolation["policyName"] = polViol["policyName"]
            
            policyViolation.update(appVApp)
            policyViolation["OrgName"] = orgs.get(policyViolation["organizationId"])
            policyViolation.pop("id")
            policyViolation.pop("publicId")
            policyViolation.pop("contactUserName")
            policyViolation.pop("organizationId")
            policyViolation["appExposure"] = appExposure
            # policyViolation["packageUrl"] = polViol["component"]["packageUrl"]
            policyViolation["displayName"] = polViol["component"]["displayName"]
            policyViolation["openTime"] = polViol["openTime"]
            policyViolation["CVE"] = CVEid

            policyViolation["policyViolationId"] = polViol["policyViolationId"]
            prevOpenTime = polViol["openTime"]                  # Comment this if you want to disable grouping
            prevPackage = polViol["component"]["packageUrl"]    # Comment this if you want to disable grouping        
            polviolationreport.append(policyViolation)

# Merge Starts

fileDate = format(datetime.now().strftime("%Y%m%d"))
print("Filedate is "+ fileDate)

dfo = pd.read_csv('output/iq_master-file.csv')  
df2 = pd.DataFrame.from_dict(polviolationreport)

df_combine = pd.merge(dfo, df2, on='policyViolationId', how='outer', indicator=True)    

for i in range(len(df_combine)):
    if df_combine.loc[i, '_merge']=='left_only' and df_combine.loc[i, 'DaysToFix'] == -1:   # This set of violations are closed today
        closeDate = datetime.strptime(fileDate, "%Y%m%d")
        df_combine.loc[i, 'ClosedDate'] = closeDate
        openDate = datetime.strptime(df_combine.loc[i, 'openTime_x'][:10], "%Y-%m-%d")
        df_combine.loc[i, 'openTime_x'] = openDate
        df_combine.loc[i, 'DaysToFix'] = abs((openDate-closeDate).days)
        #print(i)
    elif df_combine.loc[i, '_merge']=='right_only':                                         # This set of violations are newly opened today
        df_combine.loc[i, 'threatLevel_x'] = df_combine.loc[i, 'threatLevel_y']
        df_combine.loc[i, 'policyName_x'] = df_combine.loc[i, 'policyName_y']
        df_combine.loc[i, 'name_x'] = df_combine.loc[i, 'name_y']
        df_combine.loc[i, 'OrgName_x'] = df_combine.loc[i, 'OrgName_y']
        df_combine.loc[i, 'appExposure_x'] = df_combine.loc[i, 'appExposure_y']
        df_combine.loc[i, 'displayName_x'] = df_combine.loc[i, 'displayName_y']
        openDate = datetime.strptime(df_combine.loc[i, 'openTime_y'][:10], "%Y-%m-%d")
        df_combine.loc[i, 'openTime_x'] = openDate
        df_combine.loc[i, 'CVE_x'] = df_combine.loc[i, 'CVE_y']
        df_combine.loc[i, 'DaysToFix'] = -1
    #else:                                                                                  # This set of violations are closed previously or not changed
        #openDate = datetime.strptime(df_combine.loc[i, 'openTime_x'][:10], "%Y-%m-%d")
        #df_combine.loc[i, 'openTime_x'] = openDate

df_combine.drop(['threatLevel_y', 'policyName_y', 'name_y', 'OrgName_y', 'appExposure_y', 'displayName_y', 'openTime_y', 'CVE_y'], axis = 1, inplace = True)
df_combine.to_csv(f'output/iq_master-file-{fileDate}.csv', header=['threatLevel', 'policyName', 'name', 'OrgName', 'appExposure', 'displayName', 'openTime', 'CVE', 'policyViolationId', 'ClosedDate', 'DaysToFix','_merge'], index=False)
df_combine.drop(['_merge'], axis = 1, inplace = True)
df_combine.to_excel('output/iq_master-file.xlsx', header=['threatLevel', 'policyName', 'name', 'OrgName', 'appExposure', 'displayName', 'openTime', 'CVE', 'policyViolationId', 'ClosedDate', 'DaysToFix'], index=False)
df_combine.to_csv('output/iq_master-file.csv', header=['threatLevel', 'policyName', 'name', 'OrgName', 'appExposure', 'displayName', 'openTime', 'CVE', 'policyViolationId', 'ClosedDate', 'DaysToFix'], index=False)

savecsvreport(polviolationreport)

