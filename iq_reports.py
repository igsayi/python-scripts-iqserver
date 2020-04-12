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
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.csv'
    report_data = open(reportfile, 'w', newline='')
    csvwriter = csv.writer(report_data)
    header = csvrecords[0].keys()
    csvwriter.writerow(header)
    for rep_record in csvrecords:
        csvwriter.writerow(rep_record.values())
    report_data.close()

#apps = iq_session.get(f'{iq_url}/api/v2/applications?publicId=BREJBOSSDeployTest').json()["applications"]
apps = iq_session.get(f'{iq_url}/api/v2/applications').json()["applications"]
finalreport = []
for app in apps:
    publicId = app["publicId"]
    app_id = app["id"]
    reports = iq_session.get(f'{iq_url}/api/v2/reports/applications/{app_id}').json()
    for report in reports:
        report["appPublicId"] = publicId
        finalreport.append(dict(report))
savecsvreport("Reports-list", finalreport)

