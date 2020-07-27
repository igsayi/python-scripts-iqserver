from iq_common import iq_session as iq_session
from iq_common import savecsvreport as savecsvreport
from iq_common import saveOutput as saveOutput

iq_url = "https://iqserver.standard.com"

orgsl = iq_session.get(f'{iq_url}/api/v2/organizations').json()["organizations"]
orgs = {}
for org in orgsl:
    orgs.update({org["id"]: org["name"]})


orgtagslist = iq_session.get(f'{iq_url}/api/v2/organizations/ROOT_ORGANIZATION_ID').json()["tags"]
for otl in orgtagslist:
    if otl["name"] == "Internal":
        internalTag = otl["id"]
    if otl["name"] == "Distributed":
        distributedTag = otl["id"]
    if otl["name"] == "Remediated":
        remediatedTag = otl["id"]
    if otl["name"] == "Hosted":
        hostedTag = otl["id"]

#apps = iq_session.get(f'{iq_url}/api/v2/applications?publicId=PDM7').json()["applications"]
apps = iq_session.get(f'{iq_url}/api/v2/applications').json()["applications"]

componentReport = []

for app in apps:
    
    app_id = app["id"]
    app["organization"] = orgs.get(app["organizationId"])
    app["app_internal"] = ""
    app["app_Distributed"] = ""
    app["app_remediated"] = ""
    app["app_hosted"] = ""
    
    for apptag in app["applicationTags"]:
        if apptag["tagId"] == internalTag:
            app["app_internal"] = "Inernal"
        if apptag["tagId"] == distributedTag:
            app["app_Distributed"] = "Distributed"
        if apptag["tagId"] == remediatedTag:
            app["app_remediated"] = "Remediated"
        if apptag["tagId"] == hostedTag:
            app["app_hosted"] = "Hosted"
    app.pop("organizationId")
    app.pop("applicationTags")
    app.pop("id")
    
savecsvreport("appReport", apps)