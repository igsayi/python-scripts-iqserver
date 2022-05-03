
from iq_common import saveOutput as saveOutput
import math
##################
import requests
import getpass
from datetime import datetime
import json
import csv
import os

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
#    if otl["name"] == "Remediated":
#        remediatedTag = otl["id"]
#    if otl["name"] == "Hosted":
#        hostedTag = otl["id"]
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
#    app["app_remediated"] = ""
#    app["app_hosted"] = ""
    app["app_ExistingSystem"] = ""
    app["app_NewSystem"] = ""    
    
    for apptag in app["applicationTags"]:
        if apptag["tagId"] == internalTag:
            app["app_internal"] = "Inernal"
            app["appExposure"] = "Internal"
        if apptag["tagId"] == distributedTag:
           app["app_Distributed"] = "Distributed"
           app["appExposure"] = "External"
#        if apptag["tagId"] == remediatedTag:
#           app["app_remediated"] = "Remediated"
#        if apptag["tagId"] == hostedTag:
#           app["app_hosted"] = "Hosted"
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
def myFunc(e):
  return e['openTime']

def myFunc1(e):
  return e['component']

iq_url = "https://iqserver.standard.com"

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
        # polViolations.sort(key=myFunc)
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

#CVE description Search

            if CVEid is not None and len(CVEid) > 0:
                cve = iq_session.get(f'{iq_url}/api/v2/vulnerabilities/{CVEid}').json()
                #policyViolation["vulnerabilityLink"] = cve["vulnerabilityLink"]
                policyViolation["source"] = cve["source"]["shortName"]
                policyViolation["mainSeveritySource"] = cve["mainSeverity"]["source"]
                policyViolation["mainSeverityScore"] = cve["mainSeverity"]["score"]
                policyViolation["mainSeverityVector"] = cve["mainSeverity"]["vector"]

                #searchStrings = ["Memory Corruption", "Memory Handling", "Code Execution", "Buffer Overflow", "Crafted Content", "Crafted Web"]
                searchStrings = ["Code Execution", "execute arbitrary code", "execute code", "Memory Corruption", "Memory Handling", "Buffer Overflow", "Crafted Content", "Crafted Web"]

                for searchString in searchStrings:
                    policyViolation[searchString] = ""
                    if searchString.lower() in cve["explanationMarkdown"].lower():
                        policyViolation[searchString] = "Yes"
                    if cve["description"] is not None and len(cve["description"]) > 0:
                        if searchString.lower() in cve["description"].lower():
                            policyViolation[searchString] = "Yes"                        

                policyViolation["cveDescription"] = cve["description"]
                policyViolation["cveExplanationMarkdown"] = cve["explanationMarkdown"]

                policyViolation["cveCategories"] = str(cve["categories"])
                
                policyViolation["exploitUrl"] = ""
                for advisory in  cve["advisories"]:
                    if advisory["referenceType"] == "ATTACK":
                        policyViolation["exploitUrl"] = str(advisory["url"])


            prevOpenTime = polViol["openTime"]                  # Comment this if you want to disable grouping
            prevPackage = polViol["component"]["packageUrl"]    # Comment this if you want to disable grouping        
            polviolationreport.append(policyViolation)

#savecsvreport(os.path.splitext(os.path.basename(__file__))[0], polviolationreport)
savecsvreport(polviolationreport)
#saveOutput("iq_policyViolations-from-policies-pols", pols)


