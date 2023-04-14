#!/bin/bash

# usage  	promote_scan.sh git_repo user_name password
# eaxample 	promote_scan.sh IAPolicyIssue xxx ppp

if [[ $# -lt 3 ]] ; then
    echo 'missing arguments'
	echo 'usage  	promote.sh git_repo user_name password'
    exit 1
fi

app_id=$1
uname=$2
passw=$3
iqserver="https://iqserver-dev.standard.com"
source_stage="stage-release"
target_stage="release"

#get the application internal id with application public id 
app_json="$(curl -u $uname:$passw --insecure --silent "$iqserver/api/v2/applications?publicId=$app_id")"
echo "app json is $app_json "
app_internal_id="$(echo $app_json | jq -r .'applications'[0].'id')"
echo "app internal id for $app_id is $app_internal_id"	
echo "##############Promoting from $source_stage to $target_stage"
post_json="$(echo '{"sourceStageId":"'"$source_stage"'","targetStageId":"'"$target_stage"'"}')"
echo "POST Json is: $post_json"

#submit the promote scan POST request and get the status url
status_json="$(curl -u $uname:$passw --insecure --silent -X POST -H "Content-Type: application/json" -H "X-CSRF-TOKEN: api" -d $post_json "$iqserver/api/v2/evaluation/applications/"$app_internal_id"/promoteScan")"
echo "status json is: $status_json"
status_url="$(echo $status_json | jq -r .'statusUrl')"
echo "status url is: $status_url"

#Check status on the promote scan after 50 sec
sleep 50
promote_status_json="$(curl -u $uname:$passw --insecure --silent "$iqserver/$status_url")"
promote_status="$(echo $promote_status_json | jq -r .'status')"
echo "status is: $promote_status"