from iq_common import iq_session as iq_session
from iq_common import savecsvreport as savecsvreport
from iq_common import saveOutput as saveOutput
from datetime import datetime
from iq_common import apps as apps

iq_url = "https://iqserver.standard.com"

finalReport = []

def days_since(d1):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.today()
    return abs((d2 - d1).days)

appWaivers = iq_session.get(f'{iq_url}/api/v2/reports/components/waivers').json()["applicationWaivers"]

for appWaiver in appWaivers:
		publicId = appWaiver["application"]["publicId"]
		for stage in appWaiver["stages"]:
			for component in stage["componentPolicyViolations"]:
				violationStage = stage["stageId"]
				packageUrl = component["component"]["packageUrl"]
				for violation in component["waivedPolicyViolations"]:
					finalReportRecord = {}
					finalReportRecord["publicId"] = publicId
					finalReportRecord["violationStage"] = violationStage
					finalReportRecord["packageUrl"] = packageUrl
					finalReportRecord["policyViolationId"] = violation["policyViolationId"]
					finalReportRecord["policyName"] = violation["policyName"]
					waiver = violation["policyWaiver"]
					finalReportRecord["isObsolete"] = waiver["isObsolete"]
					if waiver["isObsolete"]!= True:
						finalReportRecord["scopeOwnerType"] = waiver["scopeOwnerType"]
						finalReportRecord["scopeOwnerName"] = waiver["scopeOwnerName"]
						finalReportRecord["dfference"] = days_since(waiver["createTime"][:10])
					finalReportRecord["comment"] = waiver["comment"]
					finalReport.append(finalReportRecord)

saveOutput("iq_waivers", appWaivers)
savecsvreport("iq_waivers", finalReport)
