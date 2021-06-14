from iq_common import iq_session as iq_session
from iq_common import savecsvreport as savecsvreport
from iq_common import saveOutput as saveOutput
from iq_common import apps as apps
import math
import json

iq_url = "https://iqserver.standard.com"

polviolationreport = []

for app in apps:
    app_id = app["id"]

    #if app["app_internal"] == "Inernal":
    #    continue

    if app["organization"] == "Alerts and Notifications":
        continue

    if app["name"] == "AMU Ebix - TPP E-App" or app["name"] == "AMU Ebix - TPP ASAP":
        continue

    reportIds = iq_session.get(f'{iq_url}/api/v2/reports/applications/{app_id}').json()
    
    for reportId in reportIds:

        if reportId["stage"] != "release":
            continue

        repUrl   = reportId["reportDataUrl"]
        policyrepurl = str(repUrl).replace("raw", "policy")

        policyRep = iq_session.get(f'{iq_url}/{policyrepurl}').json() # this is Policy violations report
        polComponents = policyRep["components"]

        for polComponent in polComponents:
            polViolations = []
            polViolations = polComponent["violations"]
            hasCompViolations = ""            
            nextPackageUrl = ""
            nextVersion = ""
            for compViolation in polViolations:
                if compViolation["policyThreatCategory"] != "SECURITY":
                    continue
                if compViolation["waived"] == True:
                    continue
                if compViolation["policyThreatLevel"] < 6:
                    continue

                hasCompViolations = "Yes"

            if hasCompViolations == "Yes":
                compPackageUrlDict = {}
                compPackageUrlDict["packageUrl"] = polComponent["packageUrl"]
                print("package      : "+ polComponent["packageUrl"])
                iq_session.headers.update({'Content-Type': 'application/json'})
                #remComp = iq_session.post(f'{iq_url}/api/v2/components/remediation/organization/{app["organizationId"]}/', data=json.dumps(compPackageUrlDict)).json()
                remComp = iq_session.post(f'{iq_url}/api/v2/components/remediation/application/{app["id"]}/', data=json.dumps(compPackageUrlDict)).json()


                for version in remComp["remediation"]["versionChanges"]:
                    if version["type"] == "next-no-violations":
                        nextPackageUrl = version["data"]["component"]["packageUrl"]
                        nextVersion = version["data"]["component"]["componentIdentifier"]["coordinates"]["version"]

                print("Remediation  : "+ nextPackageUrl)

                secViolation = {}
                #secViolation.update(app)
                #secViolation["hash"] = polComponent["hash"]
                secViolation["organization"] = app["organization"]
                secViolation["AppName"] = app["name"]          
                secViolation["app_internal"] = app["app_internal"]          
                secViolation["displayName"] = polComponent["displayName"]
                #secViolation["matchState"] = polComponent["matchState"]
                secViolation["packageUrl"] = polComponent["packageUrl"]
                #secViolation["no-violation-packageUrl"] = nextPackageUrl
                secViolation["version"] = polComponent["componentIdentifier"]["coordinates"]["version"]
                secViolation["no-violation-version"] = nextVersion
                if secViolation["version"] != secViolation["no-violation-version"]:
                    polviolationreport.append(secViolation)

savecsvreport("iq_policyViolations-from-reports-Remediation", polviolationreport)
saveOutput("iq_policyViolations-from-reports-Remediation-rem", remComp)
saveOutput("iq_policyViolations-from-reports-Remediation-comp", polComponents)
