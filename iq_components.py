#!/usr/bin/env python
import os.path

from iq_common import apps as apps
from iq_common import iq_session as iq_session
from iq_common import saveExcelReport as saveExcelReport


def main():
    iq_url = "https://iqserver.standard.com"

    componentReport = []
    angularReport = []
    springbootReport = []
    springframeworkReport = []

    for app in apps:
        app_id = app["id"]

        reportIds = iq_session.get(f"{iq_url}/api/v2/reports/applications/{app_id}").json()

        for reportId in reportIds:
            if reportId["stage"] != "release":
                continue

            evalDate = reportId["evaluationDate"]
            repUrl = reportId["reportDataUrl"]

            # this is BOM or raw report components
            rawComponents1 = iq_session.get(f"{iq_url}/{repUrl}").json()
            rawComponents = rawComponents1["components"]
            for rawComponent in rawComponents:
                component = {}
                component["organization"] = app["organization"]
                component["appName"] = app["publicId"]
                component["appExposure"] = app["appExposure"]
                # component["Stage"] = reportId["stage"]
                # component["EvalDate"] = evalDate
                # component["hash"] = rawComponent["hash"]
                component["displayName"] = rawComponent["displayName"]
                component["packageUrl"] = rawComponent["packageUrl"]
                # component["pathname"] = str(rawComponent["pathnames"])[0:500]
                # component["proprietary"] = rawComponent["proprietary"]
                component["matchState"] = rawComponent["matchState"]
                component["format"] = ""
                component["directDependency"] = ""
                component["parentComponentPurls"] = ""
                if rawComponent["matchState"] != "unknown":
                    component["format"] = rawComponent["componentIdentifier"]["format"]
                    # component["extension"] = str(rawComponent["componentIdentifier"]["coordinates"])
                if "dependencyData" in rawComponent:
                    component["directDependency"] = rawComponent["dependencyData"]["directDependency"]
                    if "parentComponentPurls" in rawComponent["dependencyData"]:
                        component["parentComponentPurls"] = str(rawComponent["dependencyData"]["parentComponentPurls"])

                componentReport.append(component)
                component.pop("matchState")
                component.pop("format")
                component.pop("directDependency")
                component.pop("parentComponentPurls")
                component.pop("packageUrl")
                if str(component["displayName"]).startswith("org.springframework : spring-core :"):
                    springframeworkReport.append(component)
                if str(component["displayName"]).startswith("@angular/core :"):
                    angularReport.append(component)
                if str(component["displayName"]).startswith("org.springframework.boot : spring-boot :"):
                    springbootReport.append(component)

    saveExcelReport(os.path.splitext(os.path.basename(__file__))[0], componentReport)
    saveExcelReport("springframeworkReport", springframeworkReport)
    saveExcelReport("springbootReport", springbootReport)
    saveExcelReport("angularReport", angularReport)


if __name__ == "__main__":
    main()
