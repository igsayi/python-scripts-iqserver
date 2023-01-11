import getpass

import requests
from requests import Session
from requests.auth import HTTPBasicAuth

iq_session = Session()
iq_session.auth = requests.auth.HTTPBasicAuth(getpass.getuser(), getpass.getpass(prompt="Password: ", stream=None))
iq_session.verify = False
iq_session.cookies.set("CLM-CSRF-TOKEN", "api")
iq_session.headers.update({"X-CSRF-TOKEN": "api"})
iq_url = "https://iqserver.standard.com"

# for app in apps:
app_public_id = "kong-enterprise-edition"
app_id = iq_session.get(f"{iq_url}/api/v2/applications?publicId={app_public_id}").json()["applications"][0]["id"]
stageId = "release"
iq_session.headers.update({"Content-Type": "application/xml"})

file_name = "kong-cycloneDX"
reportfile = f"output/{file_name}.xml"
fileout = open(reportfile, encoding="utf-8-sig")
d = fileout.read()
fileout.close

source = "cyclone"
post_url = f"{iq_url}/api/v2/scan/applications/{app_id}/sources/{source}?stageId={stageId}"
print(post_url)
# print(d)
r = iq_session.post(f"{iq_url}/api/v2/scan/applications/{app_id}/sources/{source}?stageId={stageId}", data=d)

print(r.text)
# saveOutputxml("cycloneDx", r.text)
