import math
from os.path import basename, splitext

from iq_common import apps as apps
from iq_common import iq_session as iq_session
from iq_common import iq_url as iq_url
from iq_common import orgs as orgs
from iq_common import saveExcelReport as saveExcelReport

polviolationreport = []

pols = iq_session.get(f"{iq_url}/api/v2/policies").json()["policies"]

for pol in pols:
    if pol["policyType"] != "security":
        continue

    # if pol["threatLevel"] < 6:
    #    continue

    # pol_id = pol["id"]
    appViolations = iq_session.get(f"{iq_url}/api/v2/policyViolations?p={pol['id']}").json()["applicationViolations"]

    for appViolation in appViolations:
        appVApp = appViolation["application"]

        # if orgs.get(appVApp["organizationId"]) == "Alerts and Notifications":
        #    continue

        # if appVApp["publicId"] != "account-linking-service":
        #    continue

        appExposure = ""
        for app in apps:
            if app["id"] == appVApp["id"]:
                appExposure = app["appExposure"]

        polViolations = appViolation["policyViolations"]
        for polViol in polViolations:
            # if polViol["stageId"] != "release":
            #    continue
            # CVEid = ""
            # CVEid = polViol["constraintViolations"][0]["reasons"][0]["reference"]["value"]

            # for polcond in polViol["constraintViolations"][0]["reasons"][0]["reference"]["value"]:
            #    CVEid = polcond["reference"]["value"]

            # conReason = polcond["reason"]
            # i = conReason.find("with")
            # CVEid = conReason[28:i].strip()

            # if prevOpenTime == polViol["openTime"] and prevPackage == polViol["component"]["packageUrl"]:
            #     #policyViolation["CVE"] = policyViolation["CVE"] + "; " + CVEid
            #     CVEid = CVEid + "; " + CVEid
            #     continue

            policyViolation = {}

            policyViolation["threatLevel"] = polViol["threatLevel"]
            policyViolation["policyName"] = polViol["policyName"]
            policyViolation["stageId"] = polViol["stageId"]
            policyViolation["OrgName"] = orgs.get(appVApp["organizationId"])
            policyViolation["publicId"] = appVApp["publicId"]
            policyViolation["appName"] = appVApp["name"]
            policyViolation["Exposure"] = appExposure
            # policyViolation["packageUrl"] = polViol["component"]["packageUrl"]
            policyViolation["displayName"] = polViol["component"]["displayName"]
            policyViolation["openTime"] = polViol["openTime"]
            policyViolation["CVE"] = polViol["constraintViolations"][0]["reasons"][0]["reference"]["value"]

            policyViolation["policyViolationId"] = polViol["policyViolationId"]

            # policyViolation["hash"] = polViol["component"]["hash"]

            # if CVEid is not None and len(CVEid) > 0:
            #     cve = iq_session.get(f'{iq_url}/api/v2/vulnerabilities/{CVEid}').json()
            #     #policyViolation["vulnerabilityLink"] = cve["vulnerabilityLink"]
            #     policyViolation["source"] = cve["source"]["shortName"]
            #     policyViolation["mainSeveritySource"] = cve["mainSeverity"]["source"]
            #     policyViolation["mainSeverityScore"] = cve["mainSeverity"]["score"]
            #     policyViolation["mainSeverityVector"] = cve["mainSeverity"]["vector"]

            #     searchStrings = ["Memory Corruption", "Memory Handling", "Code Execution", "Buffer Overflow", "Crafted Content", "Crafted Web"]
            #     for searchString in searchStrings:
            #         policyViolation[searchString] = ""
            #         if searchString.lower() in cve["explanationMarkdown"].lower():
            #             policyViolation[searchString] = "Yes"
            #         if cve["description"] is not None and len(cve["description"]) > 0:
            #             if searchString.lower() in cve["description"].lower():
            #                 policyViolation[searchString] = "Yes"

            #     policyViolation["cveDescription"] = cve["description"]
            #     policyViolation["cveExplanationMarkdown"] = cve["explanationMarkdown"]

            #     policyViolation["cveCategories"] = str(cve["categories"])

            #     policyViolation["exploitUrl"] = ""
            #     for advisory in  cve["advisories"]:
            #         if advisory["referenceType"] == "ATTACK":
            #             policyViolation["exploitUrl"] = str(advisory["url"])

            polviolationreport.append(policyViolation)


saveExcelReport(splitext(basename(__file__))[0], polviolationreport)
