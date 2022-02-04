from iq_common import iq_session as iq_session
from iq_common import savecsvreport as savecsvreport
from iq_common import saveOutput as saveOutput
from datetime import datetime
from iq_common import apps as apps

iq_url = "https://iqserver.standard.com"

waivedviolations = {}
appWaivers = iq_session.get(f'{iq_url}/api/v2/reports/components/waivers').json()["applicationWaivers"]
for appWaiver in appWaivers:
		for stage in appWaiver["stages"]:
			for component in stage["componentPolicyViolations"]:
				for violation in component["waivedPolicyViolations"]:
					waiver = violation["policyWaiver"]
					waivedviolations.update({violation["policyViolationId"]:waiver["policyWaiverId"]})

saveOutput("waivedviolations", waivedviolations)
