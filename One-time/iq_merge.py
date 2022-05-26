#!/usr/bin/env python
import sys
from cmath import isnan
from datetime import datetime

import pandas as pd

fileName = sys.argv[1]
fileDate = fileName[-12:-4]
print("Filedatee is " + fileDate)

dfo = pd.read_csv(".\ex-o.csv")  # 4300 rows
df2 = pd.read_csv(f".\{fileName}")  # 5324 rows


# df_combine = df_1.merge(df_2, on='policyViolationId', how='left')

df_combine = pd.merge(dfo, df2, on="policyViolationId", how="outer", indicator=True)  # L-352 ; R-1376 ; Both-3948

# print(df_combine)

# for i in df_combine.index:

for i in range(len(df_combine)):
    if df_combine.loc[i, "_merge"] == "left_only":  # type: ignore
        # if len(str(df_combine.loc[i, 'ClosedDate'])) <= 0:
        closeDate = datetime.strptime(fileDate, "%Y%m%d")
        openDate = datetime.strptime(df_combine.loc[i, "openTime_x"][:10], "%Y-%m-%d")  # type: ignore
        df_combine.loc[i, "ClosedDate"] = closeDate
        df_combine.loc[i, "DaysToFix"] = abs((openDate - closeDate).days)
        # print(i)
    if df_combine.loc[i, "_merge"] == "right_only":  # type: ignore
        df_combine.loc[i, "threatLevel_x"] = df_combine.loc[i, "threatLevel_y"]  # type: ignore
        df_combine.loc[i, "policyName_x"] = df_combine.loc[i, "policyName_y"]  # type: ignore
        df_combine.loc[i, "name_x"] = df_combine.loc[i, "name_y"]  # type: ignore
        df_combine.loc[i, "OrgName_x"] = df_combine.loc[i, "OrgName_y"]  # type: ignore
        df_combine.loc[i, "appExposure_x"] = df_combine.loc[i, "appExposure_y"]  # type: ignore
        df_combine.loc[i, "displayName_x"] = df_combine.loc[i, "displayName_y"]  # type: ignore
        df_combine.loc[i, "openTime_x"] = df_combine.loc[i, "openTime_y"]  # type: ignore
        df_combine.loc[i, "CVE_x"] = df_combine.loc[i, "CVE_y"]  # type: ignore
        df_combine.loc[i, "DaysToFix"] = -1

df_combine.drop(
    ["threatLevel_y", "policyName_y", "name_y", "OrgName_y", "appExposure_y", "displayName_y", "openTime_y", "CVE_y", "_merge"],
    axis=1,
    inplace=True,
)
df_combine.loc[df_combine["DaysToFix"] < 0].to_csv(
    ".\ex-o.csv",
    header=[
        "threatLevel",
        "policyName",
        "name",
        "OrgName",
        "appExposure",
        "displayName",
        "openTime",
        "CVE",
        "policyViolationId",
        "ClosedDate",
        "DaysToFix",
    ],
    index=False,
)
df_combine.loc[df_combine["DaysToFix"] < 0].to_csv(
    f".\ex-o-{fileDate}.csv",
    header=[
        "threatLevel",
        "policyName",
        "name",
        "OrgName",
        "appExposure",
        "displayName",
        "openTime",
        "CVE",
        "policyViolationId",
        "ClosedDate",
        "DaysToFix",
    ],
    index=False,
)
# df_combine.loc[df_combine['DaysToFix']> 0 ].to_csv('.\output\ex-c.csv', header=['threatLevel', 'policyName', 'name', 'OrgName', 'appExposure', 'displayName', 'openTime', 'CVE', 'policyViolationId', 'ClosedDate', 'DaysToFix'],index=False)
df_combine.loc[df_combine["DaysToFix"] > 0].to_csv(".\ex-c.csv", mode="a", header=False, index=False)
