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
    if csvrecords:
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
        internalTag = otl["id"]
    if otl["name"] == "Distributed":
        distributedTag = otl["id"]
    if otl["name"] == "Remediated":
        remediatedTag = otl["id"]
    if otl["name"] == "Hosted":
        hostedTag = otl["id"]

apps = iq_session.get(f'{iq_url}/api/v2/applications?publicId=Drupal7').json()["applications"]
#apps = iq_session.get(f'{iq_url}/api/v2/applications').json()["applications"]

componentReport = []

for app in apps:
    
    app_id = app["id"]
    app["organization"] = orgs.get(app["organizationId"])
    app["app_internal"] = ""
    app["app_Distributed"] = ""
    app["app_remediated"] = ""
    app["app_hosted"] = ""
    
    for apptag in app["applicationTags"]:
        if apptag["tagId"] == internalTag:
            app["app_internal"] = "Inernal"
        if apptag["tagId"] == distributedTag:
            app["app_Distributed"] = "Distributed"
        if apptag["tagId"] == remediatedTag:
            app["app_remediated"] = "Remediated"
        if apptag["tagId"] == hostedTag:
            app["app_hosted"] = "Hosted"
    app.pop("organizationId")
    app.pop("applicationTags")
    app.pop("id")

    reportIds = iq_session.get(f'{iq_url}/api/v2/reports/applications/{app_id}').json()
    for reportId in reportIds:
        repStage = reportId["stage"]
        repUrl   = reportId["reportDataUrl"]
        repDate  = reportId["evaluationDate"]

        rawrep = iq_session.get(f'{iq_url}/{repUrl}').json() # this is BOM or raw report
        #print("rawrep :" + str(rawrep))
        
        policyrepurl = str(repUrl).replace("raw", "policy")
        #print("policyrepurl: "+ policyrepurl)
        policyrep = iq_session.get(f'{iq_url}/{policyrepurl}').json() # this is Policy violations report

        onlyComponents = rawrep["components"]
        #onlyComponents = polComponents.copy() 

        #polComponents = policyrep["components"]
        #onlyComponents = polComponents.copy() 

        for onlyComponent in onlyComponents:
            onlyComponent.pop("securityData")
            onlyComponent.pop("licenseData")
            onlyComponent.pop("componentIdentifier")
            onlyComponent["organization"] = orgs.get(policyrep["application"]["organizationId"])
            onlyComponent["appName"] = policyrep["application"]["name"]
            onlyComponent["apppublicId"] = policyrep["application"]["publicId"]
            onlyComponent["Stage"] = reportId["stage"]
            onlyComponent["pathname"] = str(onlyComponent["pathnames"])[0:100]            
            onlyComponent.pop("pathnames")
           # onlyComponent["evaluationDate"]  = reportId["evaluationDate"]
           # onlyComponent["reportDataUrl"]  = reportId["reportDataUrl"]
            componentReport.append(onlyComponent)

savecsvreport("componentReport", componentReport)