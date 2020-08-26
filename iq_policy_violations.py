from iq_common import iq_session as iq_session
from iq_common import savecsvreport as savecsvreport
from iq_common import saveOutput as saveOutput
from iq_common import apps as apps
import math

def myFunc(e):
  return e['policyThreatLevel']

iq_url = "https://iqserver.standard.com"

polviolationreport = []

for app in apps:
    app_id = app["id"]

    reportIds = iq_session.get(f'{iq_url}/api/v2/reports/applications/{app_id}').json()
    
    for reportId in reportIds:
        if reportId["stage"] != "release":
            continue

        repUrl   = reportId["reportDataUrl"]
        policyrepurl = str(repUrl).replace("raw", "policy")

        polComponents = iq_session.get(f'{iq_url}/{policyrepurl}').json()["components"] # this is Policy violations report

        for polComponent in polComponents:            
            polViolations = []
            polViolations = polComponent["violations"]
            polViolations.sort(key=myFunc)
            prevSeverity = 0
            for compViolation in polViolations:
                if compViolation["policyThreatCategory"] != "SECURITY":
                    continue
                # if compViolation["waived"]:
                #     continue
                for polCons in compViolation["constraints"]:
                    for polcond in polCons["conditions"]:
                        conReason = polcond.get("conditionReason")
                        i = conReason.find("with")
                        CVEid = conReason[28:i]

                if prevSeverity == compViolation["policyThreatLevel"]:
                    secViolation["CVE"] = secViolation["CVE"] + "; " + CVEid
                    continue
                secViolation = {}
                secViolation.update(app)
                # secViolation["organization"] = orgs.get(policyrep["application"]["organizationId"])
                # secViolation["appName"] = policyrep["application"]["name"]
                # secViolation["apppublicId"] = policyrep["application"]["publicId"]
                # secViolation["Stage"] = reportId["stage"]
                # secViolation["evaluationDate"]  = reportId["evaluationDate"]
                # secViolation["reportDataUrl"]  = reportId["reportDataUrl"]
                # secViolation["hash"] = polComponent["hash"]
                secViolation["displayName"] = polComponent["displayName"]
                secViolation["packageUrl"] = polComponent["packageUrl"]
                secViolation["proprietary"] = polComponent["proprietary"]                                
                secViolation["matchState"] = polComponent["matchState"]
                secViolation["policyThreatCategory"] = compViolation["policyThreatCategory"]                    
                secViolation["policyName"] = compViolation["policyName"]
                secViolation["policyThreatLevel"] = compViolation["policyThreatLevel"]
                secViolation["policyViolationId"] = compViolation["policyViolationId"]
                secViolation["CVE"] = CVEid
                # if compViolation["policyThreatCategory"] == "SECURITY":
                #     for polCons in compViolation["constraints"]:
                #         for polcond in polCons["conditions"]:
                #             conReason = polcond.get("conditionReason")
                #             i = conReason.find("with")
                #             secViolation["CVE"] = conReason[28:i]
                # secViolation["policyViolationId"] = compViolation["policyViolationId"]
                secViolation["waived"] = compViolation["waived"]
                # secViolation["grandfathered"] = compViolation["grandfathered"]
                # secViolation["pathnames"] = str(polComponent["pathnames"])[0:1000]
                polviolationreport.append(secViolation)
                #prevSeverity = compViolation["policyThreatLevel"]
            #onlyComponent.pop("violations")
            #onlyComponent.pop("componentIdentifier")
            #onlyComponent.pop("pathnames")
        #print("components in stage: "+repStage+" : "+str(onlyComponents))
        #saveOutput("onlyCompoents_file-"+repStage, onlyComponents)

savecsvreport("PolicyViolations", polviolationreport)
saveOutput("polComponents", polComponents)