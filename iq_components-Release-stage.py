#!/usr/bin/env python
import json
import os.path
from datetime import datetime

import pandas as pd
from tqdm import tqdm as tqdm

from iq_common import apps as apps
from iq_common import iq_session as iq_session
from iq_common import iq_url as iq_url
from iq_common import saveExcelReport as saveExcelReport
from iq_common import saveOutput as saveOutput


def formatDate(dt: str) -> datetime:
    if dt != None:
        return datetime.strptime(dt[:10], "%Y-%m-%d").date()


def getComponentReport() -> list:
    componentReport: list = []
    print("getComponentReport")
    for app in tqdm(apps, desc="Apps.."):
        # app_id = app["id"]

        reportIds = iq_session.get(f"{iq_url}/api/v2/reports/applications/{app['id']}").json()

        for reportId in reportIds:
            if reportId["stage"] != "release":
                continue

            evalDate = reportId["evaluationDate"]
            repUrl = reportId["reportDataUrl"]

            # this is BOM or raw report components
            rawComponents = iq_session.get(f"{iq_url}/{repUrl}").json()["components"]
            for rawComponent in rawComponents:
                component: dict = {}
                component["organization"] = app["organization"]
                component["apppublicId"] = app["publicId"]
                component["appExposure"] = app["appExposure"]
                component["Stage"] = reportId["stage"]
                component["EvalDate"] = evalDate
                component["hash"] = rawComponent["hash"]
                component["displayName"] = rawComponent["displayName"]
                component["packageUrl"] = rawComponent["packageUrl"]
                component["pathname"] = str(rawComponent["pathnames"])[0:500]
                component["proprietary"] = rawComponent["proprietary"]
                component["matchState"] = rawComponent["matchState"]
                component["format"] = ""
                component["directDependency"] = ""
                component["parentComponentPurls"] = ""
                if rawComponent["matchState"] != "unknown":
                    component["format"] = rawComponent["componentIdentifier"]["format"]
                if "dependencyData" in rawComponent:
                    component["directDependency"] = rawComponent["dependencyData"]["directDependency"]
                    if "parentComponentPurls" in rawComponent["dependencyData"]:
                        component["parentComponentPurls"] = str(rawComponent["dependencyData"]["parentComponentPurls"])

                componentReport.append(component)
    return componentReport


def getUniqueComponents(componentReport: list) -> list:
    # df1 = pd.DataFrame.from_dict(componentReport)
    # df2 = df1.get("packageUrl")
    # df3 = df2.drop_duplicates()
    uniqueComponents = list({i["packageUrl"] for i in componentReport if i["matchState"] != "unknown"})
    uniqueComponentsDict = [("packageUrl", v) for v in uniqueComponents]
    a1 = {"components": [{k: v} for (k, v) in uniqueComponentsDict]}
    return a1


def paginate(items, per_page):
    pages = [items[i : i + per_page] for i in range(0, len(items), per_page)]
    return {"total": len(items), "pages_no": len(pages), "pages": pages}
    # return pages


def getComponentDetails(a1: list) -> list:
    resultCompDetails = iq_session.post(f"{iq_url}/api/v2/components/details", data=json.dumps(a1)).json()["componentDetails"]

    componentDetailsList: list = []
    for resultCompDetail in resultCompDetails:
        componentDetails: dict = {}
        componentDetails["packageUrl"] = resultCompDetail["component"]["packageUrl"]
        componentDetails["catalogDate"] = formatDate(resultCompDetail["catalogDate"])
        componentDetails["relativePopularity"] = resultCompDetail["relativePopularity"]
        componentDetails["integrityRating"] = resultCompDetail["integrityRating"]
        componentDetails["hygieneRating"] = resultCompDetail["hygieneRating"]

        if "projectData" in resultCompDetail:
            projData = resultCompDetail["projectData"]
            componentDetails["pfirstReleaseDate"] = formatDate(projData["firstReleaseDate"])
            componentDetails["plastReleaseDate"] = formatDate(projData["lastReleaseDate"])
            if "sourceControlManagement" in projData:
                if "scmDetails" in projData["sourceControlManagement"]:
                    componentDetails["commitsPerMonth"] = projData["sourceControlManagement"]["scmDetails"]["commitsPerMonth"]
                    componentDetails["uniqueDevsPerMonth"] = projData["sourceControlManagement"]["scmDetails"]["uniqueDevsPerMonth"]
                componentDetails["scmUrl"] = projData["sourceControlManagement"]["scmUrl"]
            componentDetails["pdescription"] = projData["projectMetadata"]["description"]
        componentDetailsList.append(componentDetails)
    return componentDetailsList


def mergeComponentsAndDetails(componentReport, componentDetailsList) -> list:
    df1 = pd.DataFrame(componentReport)
    df2 = pd.DataFrame(componentDetailsList)
    df3 = df1.join(df2.set_index("packageUrl"), on="packageUrl")
    finalComponentsReport = df3.to_dict()
    return finalComponentsReport


def main():
    componentReport = getComponentReport()
    saveExcelReport("componentReport", componentReport)

    uniqueComponents = getUniqueComponents(componentReport)
    saveExcelReport("uniqueComponents", uniqueComponents)
    componentDetailsList = []
    paginatedUniqueComponents = paginate(uniqueComponents["components"], 100)
    print("PaginatedUniqueComponents.." + str(paginatedUniqueComponents["total"]))
    print("PaginatedUniqueComponents.." + str(paginatedUniqueComponents["pages_no"]))

    for ucPage in tqdm(paginatedUniqueComponents["pages"], desc="Unique Componets 100s.."):
        ucPageJSON = {"components": ucPage}
        componentDetailsList.extend(getComponentDetails(ucPageJSON))
    saveExcelReport("componentDetailsList", componentDetailsList)
    finalComponentsReport = mergeComponentsAndDetails(componentReport, componentDetailsList)
    saveExcelReport(os.path.splitext(os.path.basename(__file__))[0], finalComponentsReport)


if __name__ == "__main__":
    main()
