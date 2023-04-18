#!/usr/bin/env python
from os.path import basename, splitext

from iq_common import apps as apps
from iq_common import iq_session as iq_session
from iq_common import iq_url as iq_url
from iq_common import orgs as orgs
from iq_common import saveExcelReport as saveExcelReport


def main():

    # GET /api/v2/policyWaivers/{ownerType: application|organization|repository|repository_container}/{ownerId}
    # GET /api/v2/reports/waivers/stale

    polWaivers = []

    print("getting application waivers...")
    for app in apps:
        appId = app["id"]
        appWaivers = iq_session.get(f"{iq_url}/api/v2/policyWaivers/application/{appId}").json()
        if appWaivers is not None:
            polWaivers.extend(appWaivers)

    print("getting organization waivers...")
    for org in orgs.keys():
        orgWaivers = iq_session.get(f"{iq_url}/api/v2/policyWaivers/organization/{org}").json()
        if orgWaivers is not None:
            polWaivers.extend(orgWaivers)

    print("consolidating waivers...")
    for polWaiver in polWaivers:
        polWaiver.pop("componentIdentifier")
        polWaiver.pop("displayName")

    saveExcelReport(splitext(basename(__file__))[0], polWaivers)


if __name__ == "__main__":
    main()
