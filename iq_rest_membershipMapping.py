#!/usr/bin/env python
from os.path import basename, splitext

from iq_common import apps as apps
from iq_common import iq_session as iq_session
from iq_common import iq_url as iq_url
from iq_common import orgs as orgs
from iq_common import saveExcelReport as saveExcelReport


def processRoles(ownerId: str, roles2Process: list) -> list:
    processedOrgRoles: list = []
    for role in roles2Process:
        for memberByOwner in role.get("membersByOwner"):
            if memberByOwner["ownerId"] == ownerId:
                for member in memberByOwner["members"]:
                    processedRole = {}
                    processedRole["role"] = role.get("roleName")
                    processedRole["ownerName"] = memberByOwner.get("ownerName")
                    processedRole["ownerType"] = memberByOwner.get("ownerType")
                    processedRole.update(member)
                    processedOrgRoles.append(processedRole)
            else:
                continue
    return processedOrgRoles


def main():
    # https://iqserver.standard.com/rest/membershipMapping/organization/84ee4343c8844b5ba28101387e5ac4c2
    # https://iqserver.standard.com/rest/membershipMapping/organization/ROOT_ORGANIZATION_ID

    roleMemberships: list = []

    print("getting organization roleMemberships...")
    for org in orgs.keys():
        orgRoles = iq_session.get(f"{iq_url}/rest/membershipMapping/organization/{org}").json()

        if orgRoles is not None:
            processedOrgRoles = processRoles(org, orgRoles["membersByRole"])
            roleMemberships.extend(processedOrgRoles)

    print("getting application roleMemberships...")
    for app in apps:
        appId = app["id"]
        appRoles = iq_session.get(f"{iq_url}/rest/membershipMapping/application/{appId}").json()
        if appRoles is not None:
            processedAppRoles = processRoles(app["publicId"], appRoles["membersByRole"])
            roleMemberships.extend(processedAppRoles)

    saveExcelReport(splitext(basename(__file__))[0], roleMemberships)


if __name__ == "__main__":
    main()
