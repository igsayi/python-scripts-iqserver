#!/usr/bin/env python
from os.path import basename, splitext

from iq_common import apps as apps
from iq_common import iq_session as iq_session
from iq_common import iq_url as iq_url
from iq_common import saveExcelReport as saveExcelReport
from iq_common import saveOutput as saveOutput


def main():

    finalReport = []

    waivers = iq_session.get(f"{iq_url}/api/v2/reports/components/waivers").json()
    appWaivers = waivers["applicationWaivers"]
    for appWaiver in appWaivers:
        publicId = appWaiver["application"]["publicId"]
        for stage in appWaiver["stages"]:
            for component in stage["componentPolicyViolations"]:
                violationStage = stage["stageId"]
                packageUrl = component["component"]["packageUrl"]
                displayName = component["component"]["displayName"]
                for violation in component["waivedPolicyViolations"]:
                    finalReportRecord = {}
                    finalReportRecord["publicId"] = publicId
                    finalReportRecord["violationStage"] = violationStage
                    finalReportRecord["packageUrl"] = packageUrl
                    finalReportRecord["displayName"] = displayName
                    finalReportRecord["policyId"] = violation["policyId"]
                    finalReportRecord["policyName"] = violation["policyName"]
                    finalReportRecord["policyViolationId"] = violation["policyViolationId"]
                    finalReportRecord["threatLevel"] = violation["threatLevel"]
                    waiver = violation["policyWaiver"]
                    if "displayName" in waiver:
                        waiver.pop("displayName")
                    if "componentIdentifier" in waiver:
                        waiver.pop("componentIdentifier")
                    finalReportRecord.update(waiver)

                    finalReport.append(finalReportRecord)

    saveExcelReport(splitext(basename(__file__))[0], finalReport)
    # saveOutput("iq_component_waivers", waivers)


if __name__ == "__main__":
    main()
