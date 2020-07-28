from iq_common import iq_session as iq_session
from iq_common import savecsvreport as savecsvreport
from iq_common import saveOutput as saveOutput
from iq_common import apps as apps
import math

def myFunc(e):
  return e['severity']

iq_url = "https://iqserver.standard.com"

securitydataReport = []

for app in apps:
    app_id = app["id"]

    reportIds = iq_session.get(f'{iq_url}/api/v2/reports/applications/{app_id}').json()
    
    for reportId in reportIds:
        if reportId["stage"] != "release":
            continue

        repUrl   = reportId["reportDataUrl"]

        rawComponents = iq_session.get(f'{iq_url}/{repUrl}').json()["components"] # this is BOM or raw report components

        for rawComponent in rawComponents:            

                if rawComponent["securityData"] is not None and len(rawComponent["securityData"]) >0:
                        secIssues = []
                        secIssues = rawComponent["securityData"]["securityIssues"]
                        if secIssues is not None and len(secIssues) > 0:
                                secIssues.sort(key=myFunc)
                                for secIssue in secIssues:
                                        if secIssue["status"] == "Not Applicable":
                                                continue
                                        compSecurity = {}
                                        compSecurity.update(app)
                                        # compSecurity["organization"] = app["organization"]
                                        # compSecurity["apppublicId"] = app["publicId"]
                                        # compSecurity["Stage"] = reportId["stage"]
                                        # compSecurity["evaluationDate"]  = reportId["evaluationDate"]
                                        # compSecurity["reportDataUrl"]  = reportId["reportDataUrl"]
                                        # compSecurity["hash"] = rawComponent["hash"]
                                        compSecurity["displayName"] = rawComponent["displayName"]
                                        compSecurity["packageUrl"] = rawComponent["packageUrl"]
                                        # compSecurity["pathname"] = str(rawComponent["pathnames"])[0:500]     
                                        compSecurity["proprietary"] = rawComponent["proprietary"]                                
                                        compSecurity["matchState"] = rawComponent["matchState"]
                                        compSecurity["severity"] = math.trunc(secIssue["severity"])
                                        compSecurity["status"] = secIssue["status"]
                                        compSecurity["threatCategory"] = secIssue["threatCategory"]
                                        compSecurity["reference"] = secIssue["reference"]
                                        # compSecurity["url"] = secIssue["url"]
                                        securitydataReport.append(compSecurity)
savecsvreport("securitydataReport", securitydataReport)
# saveOutput("rawComponents", rawComponents)