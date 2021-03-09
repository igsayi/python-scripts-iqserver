from iq_common import iq_session as iq_session
from iq_common import savecsvreport as savecsvreport
from iq_common import apps as apps
 
iq_url = "https://iqserver.standard.com"

componentReport = []

for app in apps:
    app_id = app["id"]

    reportIds = iq_session.get(f'{iq_url}/api/v2/reports/applications/{app_id}').json()
    
    for reportId in reportIds:
        #if reportId["stage"] != "release":
        #    continue

        evalDate = reportId["evaluationDate"]
        repUrl   = reportId["reportDataUrl"]

        rawComponents = iq_session.get(f'{iq_url}/{repUrl}').json()["components"] # this is BOM or raw report components

        for rawComponent in rawComponents:      

savecsvreport("appReport", apps)