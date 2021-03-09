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
            
            complicenseData = rawComponent["licenseData"]
            if complicenseData is not None:
                declaredLicenseName = ""
                observedLicenseName = ""
                effectiveLicenseName = ""
                licenseThreatGroupName = ""
                licenseThreatGroupLevel = ""
                licenseThreatGroupCategory = ""
                for el in complicenseData["declaredLicenses"]:
                    declaredLicenseName = declaredLicenseName + ", " +el["licenseName"]
                for el in complicenseData["observedLicenses"]:
                    observedLicenseName = observedLicenseName + ", " +el["licenseName"]
                for el in complicenseData["effectiveLicenses"]:
                    effectiveLicenseName = effectiveLicenseName + ", " +el["licenseName"]                                        
                
                for elt in complicenseData["effectiveLicenseThreats"]:
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

                    compLicense["declaredLicenseName"] = str(declaredLicenseName)[2:]
                    compLicense["observedLicenseName"] = str(observedLicenseName)[2:]
                    compLicense["effectiveLicenseName"] = str(effectiveLicenseName)[2:]

                    compLicense["licenseThreatGroupName"] = elt["licenseThreatGroupName"]
                    compLicense["licenseThreatGroupLevel"] = str(elt["licenseThreatGroupLevel"])
                    compLicense["licenseThreatGroupCategory"] = elt["licenseThreatGroupCategory"]

                    licensedataReport.append(compLicense)

                #     licenseThreatGroupName = licenseThreatGroupName + ", " + elt["licenseThreatGroupName"]
                #     licenseThreatGroupLevel = licenseThreatGroupLevel + ", " + str(elt["licenseThreatGroupLevel"])
                #     licenseThreatGroupCategory = licenseThreatGroupCategory + ", " + elt["licenseThreatGroupCategory"]                
                # compLicense["licenseThreatGroupName"] = str(licenseThreatGroupName)[2:]
                # compLicense["licenseThreatGroupLevel"] = str(licenseThreatGroupLevel)[2:]
                # compLicense["licenseThreatGroupCategory"] = str(licenseThreatGroupCategory)[2:]                    
savecsvreport("licensedataReport", licensedataReport)