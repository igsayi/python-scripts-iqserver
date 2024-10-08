import csv
import getpass
import json
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv
from requests import Session
from requests.auth import HTTPBasicAuth

dotenv_path = os.path.join(os.path.dirname(__file__), "sayi.env")
if load_dotenv(dotenv_path):
    iq_user: str = os.getenv("IQ_USERNAME", "")
    iq_token: str = os.getenv("IQ_TOKEN", "")
    iq_url: str = os.getenv("IQ_URL", "")
else:
    print("Cannot find IQ .env file")
    exit()

iq_session = Session()
# iq_session.auth = HTTPBasicAuth(getpass.getuser(), getpass.getpass(prompt="Password: ", stream=None))
iq_session.auth = HTTPBasicAuth(iq_user, iq_token)
iq_session.verify = "hlblbclmp001-standard-com-chain.pem"
iq_session.cookies.set("CLM-CSRF-TOKEN", "api")
iq_session.headers.update({"X-CSRF-TOKEN": "api"})
iq_session.headers.update({"Content-Type": "application/json"})


try:
    # response = iq_session.get(f"{iq_url}/api/v2/applications?publicId=account-linking-service")
    response = iq_session.get(f"{iq_url}/api/v2/applications")
    response.raise_for_status()

except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
    print("Cannot find IQ Server, check URL")
    exit()

except requests.exceptions.HTTPError:
    print("Could not authenticate, check username and password")
    exit()

apps = response.json()["applications"]

orgs = {}
for org in iq_session.get(f"{iq_url}/api/v2/organizations").json()["organizations"]:
    orgs.update({org["id"]: org["name"]})

roles = {}
for role in iq_session.get(f"{iq_url}/api/v2/roles").json()["roles"]:
    roles.update({role["id"]: role["name"]})

orgtags = {}
for orgtag in iq_session.get(f"{iq_url}/api/v2/organizations/ROOT_ORGANIZATION_ID").json()["tags"]:
    orgtags.update({orgtag["id"]: orgtag["name"]})

# Enrich Apps
for app in apps:
    app["organization"] = orgs.get(app["organizationId"])
    app["appExposure"] = ""
    for apptag in app["applicationTags"]:
        match orgtags.get(apptag["tagId"]):
            case "Internal":
                app["appExposure"] = "Internal"
            case "Distributed":
                app["appExposure"] = "External"
    app.pop("contactUserName")
    app.pop("applicationTags")

apps1: dict[str, dict] = {}
for app in apps:
    apps1.update({app["id"]: app})


def savecsvreport(file_name, csvrecords):
    if not os.path.exists("output"):
        os.mkdir("output")
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.csv'
    report_data = open(reportfile, "w", encoding="utf-8", newline="")
    csvwriter = csv.writer(report_data)
    if csvrecords:
        header = csvrecords[0].keys()
        csvwriter.writerow(header)
    for rep_record in csvrecords:
        csvwriter.writerow(rep_record.values())
    report_data.close()


def saveOutput(file_name, d):
    if not os.path.exists("output"):
        os.mkdir("output")
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.json'
    fileout = open(reportfile, "w")
    fileout.write(json.dumps(d, indent=4))
    fileout.close


def saveOutputxml(file_name, d):
    if not os.path.exists("output"):
        os.mkdir("output")
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.xml'
    fileout = open(reportfile, "w")
    fileout.write(d)
    fileout.close


def saveExcelReport(file_name, d):
    if not os.path.exists("output"):
        os.mkdir("output")
    df = pd.DataFrame.from_dict(d)
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.xlsx'
    df.to_excel(reportfile, index=False)


if __name__ == "__main__":
    saveExcelReport("appReport", apps)
