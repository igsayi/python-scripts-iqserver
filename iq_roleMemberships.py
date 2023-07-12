#!/usr/bin/env python
from os.path import basename, splitext

from iq_common import apps as apps
from iq_common import apps1 as apps1
from iq_common import iq_session as iq_session
from iq_common import iq_url as iq_url
from iq_common import orgs as orgs
from iq_common import roles as roles
from iq_common import saveExcelReport as saveExcelReport


def processRoles(ownerId: str, roles2Process: list) -> list:
    processedOrgRoles: list = []
    for role in roles2Process:
        for member in role["members"]:
            processedRole = {}
            if member["ownerId"] == ownerId:
                processedRole["role"] = roles.get(role["roleId"])
                if member["ownerType"] == "ORGANIZATION":
                    processedRole["ownerName"] = orgs.get(member["ownerId"])
                elif member["ownerType"] == "APPLICATION":
                    if member["ownerId"] is not None:
                        processedRole["ownerName"] = apps1.get(member["ownerId"], "").get("publicId", "")
                member.pop("ownerId")
                processedRole.update(member)
                processedOrgRoles.append(processedRole)
            else:
                continue
    return processedOrgRoles


def main():
    # https://iqserver.standard.com/api/v2/roleMemberships/global
    # https://iqserver.standard.com/api/v2/roleMemberships/organization/ROOT_ORGANIZATION_ID
    # https://iqserver.standard.com/api/v2/roles

    roleMemberships: list = []

    print("getting organization roleMemberships...")
    for org in orgs.keys():
        orgRoles = iq_session.get(f"{iq_url}/api/v2/roleMemberships/organization/{org}").json()

        if orgRoles is not None:
            processedOrgRoles = processRoles(org, orgRoles["memberMappings"])
            roleMemberships.extend(processedOrgRoles)

    print("getting application roleMemberships...")
    for app in apps:
        appId = app["id"]
        appRoles = iq_session.get(f"{iq_url}/api/v2/roleMemberships/application/{appId}").json()
        if appRoles is not None:
            processedAppRoles = processRoles(appId, appRoles["memberMappings"])
            roleMemberships.extend(processedAppRoles)

    saveExcelReport(splitext(basename(__file__))[0], roleMemberships)


if __name__ == "__main__":
    main()
