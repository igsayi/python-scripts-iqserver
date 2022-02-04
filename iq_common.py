import requests
import getpass
from datetime import datetime
import json
import csv
import os

iq_session = requests.Session()
uPass = 'Janu2022$'
# uPass = getpass.getpass(prompt='Password: ', stream=None)
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
    if otl["name"] == "Remediated":
        remediatedTag = otl["id"]
    if otl["name"] == "Hosted":
        hostedTag = otl["id"]
    if otl["name"] == "Existing Systems":
        ExistingSystemTag = otl["id"]
    if otl["name"] == "New Systems":
        NewSystemTag = otl["id"]

apps = iq_session.get(f'{iq_url}/api/v2/applications?publicId=Cloud-Acceleration-Team_service').json()["applications"]
#apps = iq_session.get(f'{iq_url}/api/v2/applications?publicId=IDI-DIPOLI').json()["applications"]
#apps = iq_session.get(f'{iq_url}/api/v2/applications').json()["applications"]

# Enrich Apps
for app in apps:
    app["organization"] = orgs.get(app["organizationId"])
    app["app_internal"] = ""
    app["app_Distributed"] = ""
    app["app_remediated"] = ""
    app["app_hosted"] = ""
    app["app_ExistingSystem"] = ""
    app["app_NewSystem"] = ""    

    
    for apptag in app["applicationTags"]:
        if apptag["tagId"] == internalTag:
            app["app_internal"] = "Inernal"
        if apptag["tagId"] == distributedTag:
           app["app_Distributed"] = "Distributed"
        if apptag["tagId"] == remediatedTag:
           app["app_remediated"] = "Remediated"
        if apptag["tagId"] == hostedTag:
           app["app_hosted"] = "Hosted"
        if apptag["tagId"] == ExistingSystemTag:
           app["app_ExistingSystem"] = "ExistingSystem"
        if apptag["tagId"] == NewSystemTag:
           app["app_NewSystem"] = "NewSystem"                      
    #app.pop("organizationId")
    app.pop("contactUserName")
    #app.pop("applicationTags")
    #app.pop("id")    

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

def saveOutputxml(file_name, d):
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.xml'
    fileout = open(reportfile,"w")
    fileout.write(d)
    fileout.close