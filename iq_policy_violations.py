import requests
import getpass
from datetime import datetime
import json
import csv
import os

iq_session = requests.Session()
iq_session.auth = requests.auth.HTTPBasicAuth(getpass.getuser(), "July2020$") # getpass.getpass(prompt='Password: ', stream=None))
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

apps = iq_session.get(f'{iq_url}/api/v2/applications?publicId=Drupal7').json()["applications"]
#apps = iq_session.get(f'{iq_url}/api/v2/applications').json()["applications"]

polviolationreport = []

for app in apps:
    app_id = app["id"]
    app["app_internal"] = ""
    for apptag in app["applicationTags"]:
        if apptag["tagId"] == internaltag:
            app["app_internal"] = "Inernal"

    reportIds = iq_session.get(f'{iq_url}/api/v2/reports/applications/{app_id}').json()
    for reportId in reportIds:
        #repStage = reportId["stage"]
        repUrl   = reportId["reportDataUrl"]

        rawrep = iq_session.get(f'{iq_url}/{repUrl}').json() # this is BOM or raw report
        
        policyrepurl = str(repUrl).replace("raw", "policy")
        policyrep = iq_session.get(f'{iq_url}/{policyrepurl}').json() # this is Policy violations report
        polComponents = policyrep["components"]

        for polComponent in polComponents:
            for compViolation in polComponent["violations"]:
                secViolation = {}
                if compViolation["policyThreatCategory"] != "SECURITY":
                    compViolation.clear()
                else:    
                    secViolation["organization"] = orgs.get(policyrep["application"]["organizationId"])
                    secViolation["appName"] = policyrep["application"]["name"]
                    secViolation["apppublicId"] = policyrep["application"]["publicId"]
                    secViolation["Stage"] = reportId["stage"]
                    #secViolation["evaluationDate"]  = reportId["evaluationDate"]
                    #secViolation["reportDataUrl"]  = reportId["reportDataUrl"]
                    secViolation["hash"] = polComponent["hash"]
                    secViolation["displayName"] = polComponent["displayName"]
                    secViolation["packageUrl"] = polComponent["packageUrl"]
                    secViolation["proprietary"] = polComponent["proprietary"]                                
                    secViolation["matchState"] = polComponent["matchState"]
                    secViolation["policyThreatCategory"] = compViolation["policyThreatCategory"]                    
                    secViolation["policyName"] = compViolation["policyName"]
                    secViolation["policyThreatLevel"] = compViolation["policyThreatLevel"]
                    secViolation["CVE"] = ""
                    if compViolation["policyThreatCategory"] == "SECURITY":
                        for polCons in compViolation["constraints"]:
                            for polcond in polCons["conditions"]:
                                conReason = polcond.get("conditionReason")
                                i = conReason.find("with")
                                secViolation["CVE"] = conReason[28:i]
                    #secViolation["policyViolationId"] = compViolation["policyViolationId"]
                    secViolation["waived"] = compViolation["waived"]
                    #secViolation["grandfathered"] = compViolation["grandfathered"]
                    secViolation["pathnames"] = str(polComponent["pathnames"])[0:1000]
                    polviolationreport.append(secViolation)
            #onlyComponent.pop("violations")
            #onlyComponent.pop("componentIdentifier")
            #onlyComponent.pop("pathnames")
        #print("components in stage: "+repStage+" : "+str(onlyComponents))
        #saveOutput("onlyCompoents_file-"+repStage, onlyComponents)

savecsvreport("PolicyViolations", polviolationreport)
saveOutput("Policy-Violations", policyrep)