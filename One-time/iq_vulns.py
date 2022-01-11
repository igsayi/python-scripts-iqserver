import requests
import getpass
from datetime import datetime
import json
import csv
import os

iq_session = requests.Session()

#uPass = 'xxxx'
uPass = getpass.getpass(prompt='Password: ', stream=None)
iq_session.auth = requests.auth.HTTPBasicAuth(getpass.getuser(), uPass)
iq_session.verify = 'hlblbclmp001-standard-com-chain.pem'
iq_session.cookies.set('CLM-CSRF-TOKEN', 'api')
iq_session.headers.update({'X-CSRF-TOKEN': 'api'})
iq_session.headers.update({'Content-Type': 'application/json'})

iq_url = "https://iqserver.standard.com"

#apps = iq_session.get(f'{iq_url}/api/v2/applications?publicId=Drupal8').json()["applications"]
apps = iq_session.get(f'{iq_url}/api/v2/applications').json()["applications"]

def saveOutput(file_name, d):
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.json'
    fileout = open(reportfile,"w")
    fileout.write(json.dumps(d, indent=4))
    fileout.close

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
 
datafile = 'output/vuln-list.json'
filein = open(datafile,"r")
vulnList = json.loads(filein.read())
filein.close

#print("AppName: "+str(apps))
cveInfoList = []
#print('Update: '+ str(apps))
for vuln in vulnList:
    cve = iq_session.get(f'{iq_url}/api/v2/vulnerabilities/{vuln}').json()
    cveInfo = {}
    cveInfo["identifier"] = cve["identifier"]

    cveInfo.setdefault("cve_cvss_2", "")
    cveInfo.setdefault("cve_cvss_3", "")
    cveInfo.setdefault("cve_cvss_2", "")
    cveInfo.setdefault("sonatype_cvss_3", "")

    for severityScore in cve["severityScores"]:
        cveInfo.update({severityScore["source"]:severityScore["score"]})

    cveInfo.update({cve["mainSeverity"]["source"]:cve["mainSeverity"]["score"]})
    cveInfo["mainseveritySource"] = cve["mainSeverity"]["source"]
    cveInfo["mainseverityScore"] = cve["mainSeverity"]["score"]
    cveInfo["mainseverityVector"] = cve["mainSeverity"]["vector"]
    cveInfo["cveCategories"] = str(cve["categories"])
    cveInfo["description"] = cve["description"]
    cveInfo["explanation"] = cve["explanationMarkdown"]
    cveInfo["detection"] = cve["detectionMarkdown"]
    cveInfo["recommendation"] = cve["recommendationMarkdown"]
    cveInfo["advisories"] = str(cve["advisories"])

    cveInfoList.append(cveInfo)

saveOutput("iq_vulns", cveInfoList)
saveOutput("iq_vulns_cve", cve)
savecsvreport("iq_vulns", cveInfoList)


