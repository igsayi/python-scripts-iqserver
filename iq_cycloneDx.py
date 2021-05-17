from iq_common import iq_session as iq_session
from iq_common import saveOutputxml as saveOutputxml
from iq_common import apps as apps
 
iq_url = "https://iqserver.standard.com"

for app in apps:
    app_id = app["id"]
    stageId = "release"

    r = iq_session.get(f'{iq_url}/api/v2/cycloneDx/{app_id}/stages/{stageId}')
    print(r.text)
    saveOutputxml("cycloneDx", r.text)
