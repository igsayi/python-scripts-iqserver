import getpass
import json
import os

import pandas as pd
from dotenv import load_dotenv
from requests import Session
from requests.auth import HTTPBasicAuth
from requests.packages import urllib3

load_dotenv()
iq_user = os.getenv("IQ_USERNAME")
iq_token = os.getenv("IQ_TOKEN")
iq_url = os.getenv("IQ_URL")

# pylint: disable=maybe-no-member
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

iq_session = Session()
# iq_session.auth = HTTPBasicAuth(getpass.getuser(), getpass.getpass(prompt="Password: ", stream=None))
iq_session.auth = HTTPBasicAuth(iq_user, iq_token)

iq_session.verify = False
iq_session.cookies.set("CLM-CSRF-TOKEN", "api")
iq_headers = {"X-CSRF-TOKEN": "api"}
iq_url = "https://iqserver.standard.com"

# GET https://iqserver.standard.com/rest/repositories/
# POST https://iqserver.standard.com/api/experimental/repositories/{repositoryId}/results/details
# GET https://iqserver.standard.com/rest/repositories/{repositoryId}/report/summary
# 		https://iqserver.standard.com/rest/repositories/7ea86ba373e04664894afcf283408f35/report/summary
# GET https://iqserver.standard.com/rest/repositories/{repositoryId}/report/details
# GET https://iqserver.standard.com/rest/ci/componentDetails/repository/54b385c856844d269491428f9301399b?componentIdentifier={"format":"pypi","coordinates":{"extension":"tar.gz","name":"request","qualifier":"","version":"1.0.117"}}&hash=c368b87ddaa215d27c61&matchState=exact&pathname=packages/request/1.0.117/request-1.0.117.tar.gz&timestamp=1668490662828

repos = iq_session.get(f"{iq_url}/rest/repositories/").json()["repositories"]

finalReport = []
rCompHash = ""
for repo in repos:
    repoId = repo["repository"]["id"]
    repo_publicId = repo["repository"]["publicId"]
    # if repo_publicId != "npmjs":
    #     continue

    repo_format = repo["repository"]["format"]
    print("repo_publicId: " + repo_publicId)
    # report = iq_session.get(f"{iq_url}/rest/repositories/{repoId}/report/summary").json()
    repositoryComponents = iq_session.get(f"{iq_url}/rest/repositories/{repoId}/report/details").json()
    # repCompHashes = list(set([{x["hash"], x["componentIdentifier"]} for x in repositoryComponents if x["threatLevel"] > 9]))

    # print("repositoryComponent: " + str(repositoryComponents[3]))
    # print("Hashes: " + str(repCompHashes[3]))

    for rComp in repositoryComponents:

        if rComp["threatLevel"] < 8:
            continue
        if rComp["highestThreatLevel"] == False:
            continue
        rCompHash = rComp["hash"]
        rCompMatchState = rComp["matchState"]
        rCompPathName = rComp["pathname"]
        compId = str(rComp["componentIdentifier"]).replace("'", '"')

        rComp["repo_publicId"] = repo_publicId
        rComp.pop("componentIdentifier")

        finalurl = f"{iq_url}/rest/ci/componentDetails/repository/{repoId}?componentIdentifier={compId}&hash={rCompHash}&matchState={rCompMatchState}&pathname={rCompPathName}"
        # print("Finalurl is: " + finalurl)

        rCompDetails = iq_session.get(finalurl).json()
        # print("rCompDetails is: " + str(rCompDetails))

        CVEs = ""
        if rCompDetails["securityVulnerabilities"] != None:
            for secVuln in rCompDetails["securityVulnerabilities"]:
                if secVuln["severity"] < 8:
                    continue
                if len(CVEs) > 0:
                    CVEs = CVEs + "; " + secVuln["refId"] + " - " + str(secVuln["severity"])
                else:
                    CVEs = secVuln["refId"] + " - " + str(secVuln["severity"])
        rComp["CVEs"] = CVEs
        finalReport.append(rComp)
        # break

with open(f"output/iq_repository_{repo_publicId}_repositoryComponents.json", "w") as outfile:
    json.dump(finalReport, outfile)

# with open(f"output/iq_repository_{repo_publicId}_repositoryComponents.json", "w") as outfile:
#    json.dump(repositoryComponents, outfile)

# with open(f"output/iq_repository_{repo_publicId}_report_details.json", "w") as outfile1:
#    outfile1.write(rCompDetails.text)

df = pd.DataFrame.from_dict(finalReport)

df.to_excel(f"output/iq_repository_report_details.xlsx")
