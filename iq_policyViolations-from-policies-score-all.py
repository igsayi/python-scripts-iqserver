from iq_common import iq_session as iq_session
from iq_common import savecsvreport as savecsvreport
from iq_common import saveOutput as saveOutput
from iq_common import orgs as orgs
from iq_common import apps as apps
import os

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
 
    #if pol["threatLevel"] < 6:
    #    continue

    pol_id = pol["id"]
    polViolations = iq_session.get(f'{iq_url}/api/v2/policyViolations?p={pol_id}').json()
    appViolations = polViolations["applicationViolations"]

    for appViolation in appViolations:
        appVApp = appViolation["application"]
        
    #    if orgs.get(appVApp["organizationId"]) == "Alerts and Notifications":
    #        continue
        
        appExposure = "External"
        for app in apps:
            if app["id"] == appVApp["id"] and app["app_internal"] == "Inernal":
                appExposure = "Inernal"

    #    if appExposure == "Inernal":
    #        continue

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

            # if prevOpenTime == polViol["openTime"] and prevPackage == polViol["component"]["packageUrl"]:
            #     #policyViolation["CVE"] = policyViolation["CVE"] + "; " + CVEid
            #     CVEid = CVEid + "; " + CVEid
            #     continue

            policyViolation = {}
            
            policyViolation["threatLevel"] = polViol["threatLevel"]
            policyViolation["policyName"] = polViol["policyName"]
            
            policyViolation.update(appVApp)
            policyViolation["OrgName"] = orgs.get(policyViolation["organizationId"])
            policyViolation.pop("id")
            policyViolation.pop("publicId")
            policyViolation.pop("contactUserName")
            policyViolation.pop("organizationId")
            policyViolation["appExposure"] = appExposure
            # policyViolation["packageUrl"] = polViol["component"]["packageUrl"]
            policyViolation["displayName"] = polViol["component"]["displayName"]
            policyViolation["openTime"] = polViol["openTime"]
            policyViolation["CVE"] = CVEid

            policyViolation["policyViolationId"] = polViol["policyViolationId"]
            prevOpenTime = polViol["openTime"]                  # Comment this if you want to disable grouping
            prevPackage = polViol["component"]["packageUrl"]    # Comment this if you want to disable grouping        
            polviolationreport.append(policyViolation)


savecsvreport(os.path.splitext(os.path.basename(__file__))[0], polviolationreport)
#saveOutput("iq_policyViolations-from-policies-pols", pols)


