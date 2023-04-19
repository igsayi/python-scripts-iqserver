#!/usr/bin/env python
from os.path import basename, splitext

from iq_common import apps as apps
from iq_common import iq_session as iq_session
from iq_common import iq_url as iq_url
from iq_common import orgs as orgs
from iq_common import saveExcelReport as saveExcelReport
from iq_common import saveOutput


def main():

    # GET /api/v2/policyWaivers/{ownerType: application|organization|repository|repository_container}/{ownerId}
    # GET /api/v2/reports/waivers/stale

    # polWaivers = []

    print("getting stale waivers...")
    staleWaivers = iq_session.get(f"{iq_url}/api/v2/reports/waivers/stale").json()["staleWaivers"]
    for staleWaiver in staleWaivers:
        staleWaiver.pop("constraintFacts")
        if "staleEvaluations" in staleWaiver:
            staleWaiver.pop("staleEvaluations")

    saveExcelReport(splitext(basename(__file__))[0], staleWaivers)
    # saveOutput(splitext(basename(__file__))[0], staleWaivers)


if __name__ == "__main__":
    main()
