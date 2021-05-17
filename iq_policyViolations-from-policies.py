from iq_common import iq_session as iq_session
from iq_common import savecsvreport as savecsvreport
from iq_common import saveOutput as saveOutput
from iq_common import orgs as orgs
from iq_common import apps as apps

import math

def myFunc(e):
  return e['openTime']

def myFunc1(e):
  return e['component']

iq_url = "https://iqserver.standard.com"

polviolationreport = []

pols = iq_session.get(f'{iq_url}/api/v2/policies').json()["policies"]

for pol in pols:
    if pol["policyType"] != "security":
        continue
 
 #   if pol["threatLevel"] < 6:
 #       continue

    pol_id = pol["id"]
    polViolations = iq_session.get(f'{iq_url}/api/v2/policyViolations?p={pol_id}').json()
    appViolations = polViolations["applicationViolations"]

    for appViolation in appViolations:
        appVApp = appViolation["application"]
        
        #if orgs.get(appVApp["organizationId"]) == "Alerts and Notifications":
        #    continue
        
        appExposure = "External"
        for app in apps:
            if app["id"] == appVApp["id"] and app["app_internal"] == "Inernal":
                appExposure = "Inernal"

        #if appExposure == "Inernal":
        #    continue

        unsortedpolViolations = appViolation["policyViolations"] 
        # polViolations.sort(key=myFunc)
        sortedPolViolations = sorted(unsortedpolViolations, key = lambda i: (i['openTime'], i['component']["hash"])) 
        prevOpenTime = ""
        prevPackage = ""
        for polViol in sortedPolViolations:
            if polViol["stageId"] != "release":
                continue

            for polcond in polViol["constraintViolations"][0]["reasons"]:
                conReason = polcond["reason"]
                i = conReason.find("with")
                CVEid = conReason[28:i].strip()

            if prevOpenTime == polViol["openTime"] and prevPackage == polViol["component"]["packageUrl"]:
                #policyViolation["CVE"] = policyViolation["CVE"] + "; " + CVEid
                continue

            policyViolation = {}
            policyViolation.update(appVApp)
            policyViolation["OrgName"] = orgs.get(policyViolation["organizationId"])
            policyViolation.pop("id")
            policyViolation.pop("contactUserName")
            policyViolation.pop("organizationId")
            policyViolation["policyViolationId"] = polViol["policyViolationId"]
            policyViolation["Exposure"] = appExposure

            policyViolation["policyName"] = polViol["policyName"]
            policyViolation["stageId"] = polViol["stageId"]
            policyViolation["openTime"] = polViol["openTime"]
            policyViolation["packageUrl"] = polViol["component"]["packageUrl"]
            # policyViolation["hash"] = polViol["component"]["hash"]
            policyViolation["CVE"] = CVEid

            if CVEid is not None and len(CVEid) > 0:
                cve = iq_session.get(f'{iq_url}/api/v2/vulnerabilities/{CVEid}').json()
                #policyViolation["vulnerabilityLink"] = cve["vulnerabilityLink"]
                policyViolation["source"] = cve["source"]["shortName"]
                policyViolation["mainSeveritySource"] = cve["mainSeverity"]["source"]
                policyViolation["mainSeverityScore"] = cve["mainSeverity"]["score"]
                policyViolation["mainSeverityVector"] = cve["mainSeverity"]["vector"]

                searchStrings = ["Memory Corruption", "Memory Handling", "Code Execution", "Buffer Overflow", "Crafted Content", "Crafted Web"]
                for searchString in searchStrings:
                    policyViolation[searchString] = ""
                    if searchString.lower() in cve["explanationMarkdown"].lower():
                        policyViolation[searchString] = "Yes"
                    if cve["description"] is not None and len(cve["description"]) > 0:
                        if searchString.lower() in cve["description"].lower():
                            policyViolation[searchString] = "Yes"                        

                policyViolation["cveDescription"] = cve["description"]
                policyViolation["cveExplanationMarkdown"] = cve["explanationMarkdown"]

                policyViolation["cveCategories"] = str(cve["categories"])
                
                policyViolation["exploitUrl"] = ""
                for advisory in  cve["advisories"]:
                    if advisory["referenceType"] == "ATTACK":
                        policyViolation["exploitUrl"] = str(advisory["url"])

            #prevSeverity = compViolation["policyThreatLevel"]
            prevOpenTime = polViol["openTime"]                  # Comment this if you want to disable grouping
            prevPackage = polViol["component"]["packageUrl"]    # Comment this if you want to disable grouping        
            polviolationreport.append(policyViolation)
            # print("reasons: "+ str(polViol["constraintViolations"][0]["reasons"]))

savecsvreport("iq_policyViolations-from-policies", polviolationreport)
#saveOutput("iq_policyViolations-from-policies-polViolations", polViolations)
#saveOutput("iq_policyViolations-from-policies-pols", pols)

# saveOutput("Policy", pols)
