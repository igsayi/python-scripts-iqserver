import requests
import getpass
from datetime import datetime
import json
import csv
import os

iq_session = requests.Session()
iq_session.auth = requests.auth.HTTPBasicAuth(getpass.getuser(), getpass.getpass(prompt='Password: ', stream=None))
iq_session.verify = 'hlblbclmp001-standard-com-chain.pem'
iq_session.cookies.set('CLM-CSRF-TOKEN', 'api')
iq_headers = {'X-CSRF-TOKEN': 'api'}
iq_url = "https://iqserver.standard.com"

def savecsvreport(file_name, csvrecords):
    if not os.path.exists("output"):
        os.mkdir("output")
    reportfile = f'temp/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.csv'
    report_data = open(reportfile, 'w', newline='')
    csvwriter = csv.writer(report_data)
    header = csvrecords[0].keys()
    csvwriter.writerow(header)
    for rep_record in csvrecords:
        csvwriter.writerow(rep_record.values())
    report_data.close()

def saveOutput(file_name, d):
    reportfile = f'temp/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.json'
    fileout = open(reportfile,"w")
    fileout.write(json.dumps(d, indent=4))

orgsl = iq_session.get(f'{iq_url}/api/v2/organizations').json()["organizations"]
orgs = {}
for org in orgsl:
    orgs.update({org["id"]: org["name"]})


orgtagslist = iq_session.get(f'{iq_url}/api/v2/organizations/ROOT_ORGANIZATION_ID').json()["tags"]
for otl in orgtagslist:
    if otl["name"] == "Internal":
        internaltag = otl["id"]
#print("internaltag: " + internaltag)

#apps = iq_session.get(f'{iq_url}/api/v2/applications?publicId=PDM7').json()["applications"]
apps = iq_session.get(f'{iq_url}/api/v2/applications').json()["applications"]

polviolationreport = []
for app in apps:
    #publicId = app["publicId"]
    app_id = app["id"]
    app["app_internal"] = ""
    #print(app["publicId"])
    for apptag in app["applicationTags"]:
        if apptag["tagId"] == internaltag:
            app["app_internal"] = "Inernal"

    reportIds = iq_session.get(f'{iq_url}/api/v2/reports/applications/{app_id}').json()
    for reportId in reportIds:
        repStage = reportId["stage"]
        repUrl   = reportId["reportDataUrl"]
        repDate  = reportId["evaluationDate"]

        #reportId["appPublicId"] = app["publicId"]
        #reportId["app_internal"] = app["app_internal"]
        
        #print("policyrepurl: "+ rawrepUrl)
        rawrep = iq_session.get(f'{iq_url}/{repUrl}').json() # this is BOM or raw report
        #print("rawrep :" + str(rawrep))
        #saveOutput("rawrep_file-"+repStage, rawrep)
        
        policyrepurl = str(repUrl).replace("raw", "policy")
        #print("policyrepurl: "+ policyrepurl)
        policyrep = iq_session.get(f'{iq_url}/{policyrepurl}').json() # this is Policy violations report
        #print("policyrep in Stage: "+ repStage +": " + str(policyrep))    
        #saveOutput("policyrep_file-"+repStage, policyrep)
        polComponents = policyrep["components"]
        onlyComponents = polComponents.copy() 
        for onlyComponent in onlyComponents:
            #onlyComponent.pop("violations")
            #onlyComponent.pop("componentIdentifier")
            #onlyComponent.pop("pathnames")
            for policyViolation in onlyComponent["violations"]:
                policyViolation["appName"] = policyrep["application"]["name"]
                policyViolation["apppublicId"] = policyrep["application"]["publicId"]
                policyViolation["organization"] = orgs.get(policyrep["application"]["organizationId"])
                policyViolation["Stage"] = reportId["stage"]
                policyViolation["evaluationDate"]  = reportId["evaluationDate"]
                policyViolation["reportDataUrl"]  = reportId["reportDataUrl"]
                policyViolation["packageUrl"] = onlyComponent["packageUrl"]
                policyViolation["hash"] = onlyComponent["hash"]
                policyViolation["proprietary"] = onlyComponent["proprietary"]                                
                policyViolation["matchState"] = onlyComponent["matchState"]
                policyViolation["displayName"] = onlyComponent["displayName"]
                policyViolation["CVE"] = ""
                if policyViolation["policyThreatCategory"] == "SECURITY":
                    for polCons in policyViolation["constraints"]:
                        for polcond in polCons["conditions"]:
                            conReason = polcond.get("conditionReason")
                            i = conReason.find("with")
                            policyViolation["CVE"] = conReason[28:i]
                policyViolation.pop("constraints")
                polviolationreport.append(policyViolation)

        #print("components in stage: "+repStage+" : "+str(onlyComponents))
        #saveOutput("onlyCompoents_file-"+repStage, onlyComponents)

savecsvreport("PolicyViolations", polviolationreport)


#print("reportIds: " + str(reportIds))
#savecsvreport("Reports-list", reportIds)

#print(apps)