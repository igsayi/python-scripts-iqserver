import requests
import getpass
from datetime import datetime
import json
import csv
import os

iq_session = requests.Session()

uPass = getpass.getpass(prompt='Password: ', stream=None)
iq_session.auth = requests.auth.HTTPBasicAuth(getpass.getuser(), uPass)
iq_session.verify = 'hlblbclmp001-standard-com-chain.pem'
iq_session.cookies.set('CLM-CSRF-TOKEN', 'api')
iq_session.headers.update({'X-CSRF-TOKEN': 'api'})
iq_session.headers.update({'Content-Type': 'application/json'})

iq_url = "https://iqserver.standard.com"

#apps = iq_session.get(f'{iq_url}/api/v2/applications?publicId=Drupal8').json()["applications"]
apps = iq_session.get(f'{iq_url}/api/v2/applications').json()["applications"]

def saveOutput(file_name, d):
    reportfile = f'output/{file_name}-{format(datetime.now().strftime("%Y%m%d"))}.json'
    fileout = open(reportfile,"w")
    fileout.write(json.dumps(d, indent=4))
    fileout.close
 
datafile = 'output/App-Cat.json'
filein = open(datafile,"r")
appCatList = json.loads(filein.read())
filein.close

#print("AppName: "+str(apps))

#print('Update: '+ str(apps))
for app in apps:
    #print("AppName: "+ app["name"])
    #print("AppCategory: " + appCatList.get(app["id"]))
    if appCatList.get(app["id"]) == "Existing":
        app["applicationTags"].append({"tagId": "e8e069027fdd46faa1791f794e3eced4"})
    elif appCatList.get(app["id"]) == "New":
        app["applicationTags"].append({"tagId": "f36242c553334ae6a4ac34ef952d33f9"})
    else:
        app["applicationTags"].append({"tagId": "f36242c553334ae6a4ac34ef952d33f9"})
        print("AppName - not there: "+ app["name"])
    #print("AppName : "+ str(app))
    result = iq_session.put(f'{iq_url}/api/v2/applications/{app["id"]}', data=json.dumps(app)) 
    print("AppName: "+ app["name"] + "; "+ "AppCategory: " + str(appCatList.get(app["id"])) + "; " + "result: "+ str(result.status_code))

#print('Update: '+ str(apps))

#saveOutput("AppCat", apps)

