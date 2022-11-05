#!/usr/bin/python3

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

if not os.path.exists("output"):
        os.mkdir("output")

waivers_file_name = "output/iq_waivers.json"
report_file_name = "output/iq_waivers_report.json"

report = {
	"review":60, 
	"limit":90, 
	"todo":[]
}

def get_waivers():
	url = f'{iq_url}/api/v2/reports/components/waivers'
	return iq_session.get(url).json()

def delete_waivers( ownerType, ownerId, policyWaiverId ):
	url = f'{iq_url}/rest/policyWaiver/{ownerType}/{ownerId}/{policyWaiverId}'
	return iq_session.delete(url, headers=iq_headers)

def days_since(d1):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.today()
    return abs((d2 - d1).days)

def saveOutput(file_name, d):
	with open(file_name,"w+") as file:
		file.write(json.dumps(d, indent=4))

## ----------------------------------------------------------------------------
def filterApplications():
	waivers = get_waivers()
	# saveOutput(waivers_file_name, waivers)
	for application in waivers["applicationWaivers"]:
		publicId = application["application"]["publicId"]
		for stage in application["stages"]:
			for component in stage["componentPolicyViolations"]:
				violationStage = stage["stageId"]
				processComponent(component, publicId,violationStage )

def processComponent(component, publicId, violationStage):
	packageUrl = component["component"]["packageUrl"]
	for violation in component["waivedPolicyViolations"]:
		waiver = violation["policyWaiver"]
		#if waiver["isObsolete"]:
		#	continue

		ownerId = publicId if waiver["scopeOwnerType"] == "application" else waiver["scopeOwnerId"]
		dfference = days_since(waiver["createTime"][:10])

		processWaiver({
			"publicId" : publicId, "ownerId" : ownerId, "violationStage": violationStage,
			"packageUrl" : packageUrl, "diff" : dfference,
			"policyViolationId" : violation["policyViolationId"], 
			"policyId": violation["policyId"],
			"policyName": violation["policyName"],
			"policyWaiverId" : waiver["policyWaiverId"],
			"ownerType" : waiver["scopeOwnerType"], 
			"scopeOwnerName" : waiver["scopeOwnerName"], 
			"createTime": waiver["createTime"],
			"isObsolete": waiver["isObsolete"],
			"comment": waiver["comment"]
		})

def processWaiver(waiver):
	if report["review"] > waiver["diff"]:
		waiver["todo"]="to_maintain"
		report["todo"].append(waiver)
		
	elif report["review"] <= waiver["diff"]:
		waiver["todo"]="to_review"
		report["todo"].append(waiver)

	elif report["limit"] <= waiver["diff"]:
		waiver["todo"]="to_delete"
		report["todo"].append(waiver)


filterApplications()
print( json.dumps(report, indent=4) )
# saveOutput(report_file_name, report)

reportfile = 'output/waivers-Report-{}.csv'.format(datetime.now().strftime("%Y%m%d"))
report_data = open(reportfile, 'w', newline='')
csvwriter = csv.writer(report_data)

header = report["todo"][0].keys()
csvwriter.writerow(header)
for rep_record in report["todo"]:
        csvwriter.writerow(rep_record.values())
report_data.close()

#temp = delete_waivers(waiver["ownerType"], waiver["ownerId"], waiver["policyWaiverId"])
## ----------------------------------------------------------------------------

					











