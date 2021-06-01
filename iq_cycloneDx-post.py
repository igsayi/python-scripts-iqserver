from iq_common import iq_session as iq_session
from iq_common import saveOutputxml as saveOutputxml
from iq_common import apps as apps
 
iq_url = "https://iqserver-dev.standard.com"

for app in apps:
    app_id = app["id"]
    stageId = "release"
    iq_session.headers.update({'Content-Type': 'application/xml'})
    
    file_name = "cycloneDx-20210517"
    reportfile = f'output/{file_name}.xml'
    fileout = open(reportfile,"r")
    d = fileout.read()
    fileout.close

    source = "cyclone"
    r = iq_session.post(f'{iq_url}/api/v2/scan/applications/{app_id}/sources/{source}?stageId={stageId}', data=d)

    print(r.text)
    #saveOutputxml("cycloneDx", r.text)
