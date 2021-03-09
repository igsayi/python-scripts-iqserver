from iq_common import iq_session as iq_session
from iq_common import savecsvreport as savecsvreport
from iq_common import saveOutput as saveOutput
from iq_common import apps as apps
import math

iq_url = "https://iqserver.standard.com"

polviolationreport = []

for app in apps:
    app_id = app["id"]

    if app["app_internal"] == "Inernal":
        continue

    if app["organization"] == "Alerts and Notifications" or app["organization"] == "IT-ITES":
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
            for compViolation in polViolations:
                if compViolation["policyThreatCategory"] != "SECURITY":
                    continue
                if compViolation["waived"] == "TRUE":
                    continue
                if compViolation["policyThreatLevel"] < 6:
                    continue

                secViolation = {}
                secViolation.update(app)
                # secViolation["Stage"] = reportId["stage"]
                # secViolation["evaluationDate"]  = reportId["evaluationDate"]
                # secViolation["reportDataUrl"]  = reportId["reportDataUrl"]
                #secViolation["packageUrl"] = polComponent["packageUrl"]
                #secViolation["proprietary"] = polComponent["proprietary"]                                
                #secViolation["policyThreatCategory"] = compViolation["policyThreatCategory"]                    
                #secViolation["policyName"] = compViolation["policyName"]
                secViolation["hash"] = polComponent["hash"]
                secViolation["displayName"] = polComponent["displayName"]
                secViolation["matchState"] = polComponent["matchState"]
                secViolation["policyThreatLevel"] = compViolation["policyThreatLevel"]
                secViolation["policyViolationId"] = compViolation["policyViolationId"]
                secViolation["waived"] = compViolation["waived"]
                if compViolation["policyThreatCategory"] == "SECURITY":
                    for polCons in compViolation["constraints"]:
                        for polcond in polCons["conditions"]:
                            conReason = polcond.get("conditionReason")
                            i = conReason.find("with")
                            secViolation["reference"] = conReason[28:i].strip()
                secViolation["cveCategories"] = ""
                secViolation["exploitUrl"] = ""
                cveRef = secViolation["reference"]
                if cveRef is not None and len(cveRef) > 0:
                    cve = iq_session.get(f'{iq_url}/api/v2/vulnerabilities/{cveRef}').json()
                    secViolation["cveCategories"] = str(cve["categories"])
                    for advisory in  cve["advisories"]:
                        if advisory["referenceType"] == "ATTACK":
                            secViolation["exploitUrl"] = str(advisory["url"])

                # secViolation["grandfathered"] = compViolation["grandfathered"]
                # secViolation["pathnames"] = str(polComponent["pathnames"])[0:1000]
                polviolationreport.append(secViolation)
                #prevSeverity = compViolation["policyThreatLevel"]      # Comment this if you want to disable grouping
            #onlyComponent.pop("violations")
            #onlyComponent.pop("componentIdentifier")
            #onlyComponent.pop("pathnames")
        #print("components in stage: "+repStage+" : "+str(onlyComponents))
        #saveOutput("onlyCompoents_file-"+repStage, onlyComponents)

savecsvreport("iq_policyViolations-from-reports", polviolationreport)
saveOutput("iq_policyViolations-from-reports", policyRep)