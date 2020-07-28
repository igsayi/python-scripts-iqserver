from iq_common import iq_session as iq_session
from iq_common import savecsvreport as savecsvreport
from iq_common import saveOutput as saveOutput
from iq_common import orgs as orgs
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
    pol_id = pol["id"]
    appViolations = iq_session.get(f'{iq_url}/api/v2/policyViolations?p={pol_id}').json()["applicationViolations"]
    #print("PolViol: " + str(polViolations))
    for appViolation in appViolations:
        app = appViolation["application"]
        unsortedpolViolations = appViolation["policyViolations"] 
        # polViolations.sort(key=myFunc)
        polViolations = sorted(unsortedpolViolations, key = lambda i: (i['openTime'], i['component']["packageUrl"])) 
        prevOpenTime = ""
        prevPackage = ""
        for polViol in polViolations:
            if polViol["stageId"] != "release":
                continue

            for polcond in polViol["constraintViolations"][0]["reasons"]:
                conReason = polcond["reason"]
                i = conReason.find("with")
                CVEid = conReason[28:i]

            if prevOpenTime == polViol["openTime"] and prevPackage == polViol["component"]["packageUrl"]:
                policyViolation["CVE"] = policyViolation["CVE"] + "; " + CVEid
                continue

            policyViolation = {}
            policyViolation.update(app)
            policyViolation["OrgName"] = orgs.get(policyViolation["organizationId"])
            policyViolation.pop("id")
            policyViolation.pop("contactUserName")
            policyViolation.pop("organizationId")
            # policyViolation["policyViolationId"] = polViol["policyViolationId"]
            policyViolation["policyName"] = polViol["policyName"]
            policyViolation["stageId"] = polViol["stageId"]
            policyViolation["openTime"] = polViol["openTime"]
            policyViolation["packageUrl"] = polViol["component"]["packageUrl"]
            # policyViolation["hash"] = polViol["component"]["hash"]
            policyViolation["CVE"] = CVEid
            #prevSeverity = compViolation["policyThreatLevel"]
            prevOpenTime = polViol["openTime"]
            prevPackage = polViol["component"]["packageUrl"]            
            polviolationreport.append(policyViolation)
            # print("reasons: "+ str(polViol["constraintViolations"][0]["reasons"]))
            

savecsvreport("Policy-Violations1", polviolationreport)
saveOutput("Policy-Violations1", appViolations)
saveOutput("Policy", pols)
