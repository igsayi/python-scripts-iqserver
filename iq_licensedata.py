from iq_common import iq_session as iq_session
from iq_common import savecsvreport as savecsvreport
from iq_common import apps as apps

iq_url = "https://iqserver.standard.com"

licensedataReport = []

for app in apps:
    app_id = app["id"]

    reportIds = iq_session.get(f'{iq_url}/api/v2/reports/applications/{app_id}').json()
    
    for reportId in reportIds:
        if reportId["stage"] != "release":
            continue

        repUrl   = reportId["reportDataUrl"]

        rawComponents = iq_session.get(f'{iq_url}/{repUrl}').json()["components"] # this is BOM or raw report components

        for rawComponent in rawComponents:            
            compLicense = {}

            compLicense["organization"] = app["organization"]
            compLicense["apppublicId"] = app["publicId"]
            compLicense["Stage"] = reportId["stage"]
            compLicense["evaluationDate"]  = reportId["evaluationDate"]
            compLicense["reportDataUrl"]  = reportId["reportDataUrl"]
            compLicense["hash"] = rawComponent["hash"]
            compLicense["displayName"] = rawComponent["displayName"]
            compLicense["packageUrl"] = rawComponent["packageUrl"]
            compLicense["pathname"] = str(rawComponent["pathnames"])[0:500]     
            compLicense["proprietary"] = rawComponent["proprietary"]                                
            compLicense["matchState"] = rawComponent["matchState"]

            complicenseData = rawComponent["licenseData"]
            if complicenseData is not None:
                licenseId = ""
                licenseName = ""
                licenseThreatGroupName = ""
                licenseThreatGroupLevel = ""
                licenseThreatGroupCategory = ""
                for el in complicenseData["effectiveLicenses"]:
                    licenseId = licenseId + ", " + el["licenseId"]
                    licenseName = licenseName + ", " +el["licenseName"]
                compLicense["licenseId"] = str(licenseId)[2:]
                compLicense["licenseName"] = str(licenseName)[2:]
                for elt in complicenseData["effectiveLicenseThreats"]:
                    licenseThreatGroupName = licenseThreatGroupName + ", " + elt["licenseThreatGroupName"]
                    licenseThreatGroupLevel = licenseThreatGroupLevel + ", " + str(elt["licenseThreatGroupLevel"])
                    licenseThreatGroupCategory = licenseThreatGroupCategory + ", " + elt["licenseThreatGroupCategory"]                
                compLicense["licenseThreatGroupName"] = str(licenseThreatGroupName)[2:]
                compLicense["licenseThreatGroupLevel"] = str(licenseThreatGroupLevel)[2:]
                compLicense["licenseThreatGroupCategory"] = str(licenseThreatGroupCategory)[2:]
            
            licensedataReport.append(compLicense)
savecsvreport("licensedataReport", licensedataReport)