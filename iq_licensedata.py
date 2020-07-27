from iq_common import iq_session as iq_session
from iq_common import savecsvreport as savecsvreport
from iq_common import apps as apps

iq_url = "https://iqserver.standard.com"

licensedataReport = []

for app in apps:
    app_id = app["id"]

    reportIds = iq_session.get(f'{iq_url}/api/v2/reports/applications/{app_id}').json()
    
    for reportId in reportIds:
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
            compLicense["proprietary"] = rawComponent["proprietary"]                                
            compLicense["matchState"] = rawComponent["matchState"]
            complicenseData = rawComponent["licenseData"]
            if complicenseData is not None:
                for el in complicenseData["effectiveLicenses"]:
                    compLicense["licenseId"] = el["licenseId"]
                    compLicense["licenseName"] = el["licenseName"]
                for elt in complicenseData["effectiveLicenseThreats"]:
                    compLicense["licenseThreatGroupName"] = elt["licenseThreatGroupName"]
                    compLicense["licenseThreatGroupLevel"] = elt["licenseThreatGroupLevel"]
                    compLicense["licenseThreatGroupCategory"] = elt["licenseThreatGroupCategory"]                
            
            licensedataReport.append(compLicense)
savecsvreport("licensedataReport", licensedataReport)