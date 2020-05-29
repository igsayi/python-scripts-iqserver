import requests
import getpass

# pylint: disable=maybe-no-member
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
iq_session = requests.Session()
iq_session.auth = requests.auth.HTTPBasicAuth(getpass.getuser(), getpass.getpass(prompt='Password: ', stream=None))
iq_session.verify = False
iq_session.cookies.set('CLM-CSRF-TOKEN', 'api')
iq_headers = {'X-CSRF-TOKEN': 'api'}
iq_url = "https://iqserver.standard.com"


stages = ["release"]

#apps = iq_session.get(f'{iq_url}/api/v2/applications?publicId=BREJBOSSDeployTest').json()["applications"]
apps = iq_session.get(f'{iq_url}/api/v2/applications').json()["applications"]
for app in apps:
	publicId = app["publicId"]
	app_id = app["id"]
	reports = iq_session.get(f'{iq_url}/api/v2/reports/applications/{app_id}').json()
	for report in reports:
		if report["stage"] in stages:
			report_id = report["reportHtmlUrl"].split("/")[-1]
			url = f'{iq_url}/rest/report/{publicId}/{report_id}/reevaluatePolicy'
			result = iq_session.post(url, headers=iq_headers)
			print(publicId, ': ', result.status_code == requests.codes.ok)