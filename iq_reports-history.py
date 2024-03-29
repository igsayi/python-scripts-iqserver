#!/usr/bin/env python
import os.path

from iq_common import apps as apps
from iq_common import iq_session as iq_session
from iq_common import saveExcelReport as saveExcelReport


def main():
    iq_url = "https://iqserver.standard.com"
    finalReport = []
    for app in apps:
        app_id = app["id"]
        reports = iq_session.get(f"{iq_url}/api/v2/reports/applications/{app_id}/history").json()["reports"]
        if reports is not None and len(reports) > 0:
            for report in reports:
                # if reportId["stage"] != "release":
                #    continue
                finalReportrecord = {}
                finalReportrecord.update(app)
                finalReportrecord["stage"] = report["stage"]
                finalReportrecord["evaluationDate"] = report["evaluationDate"]
                finalReportrecord["reportDataUrl"] = report["reportDataUrl"]
                finalReportrecord["policyEvaluationId"] = report["policyEvaluationId"]
                finalReportrecord["scanId"] = report["scanId"]
                finalReportrecord["isForMonitoring"] = report["isForMonitoring"]
                finalReportrecord["commitHash"] = report["commitHash"]
                finalReportrecord["affectedComponentCount"] = report["policyEvaluationResult"]["affectedComponentCount"]
                finalReportrecord["totalComponentCount"] = report["policyEvaluationResult"]["totalComponentCount"]
                finalReport.append(dict(finalReportrecord))

    saveExcelReport(os.path.splitext(os.path.basename(__file__))[0], finalReport)


if __name__ == "__main__":
    main()
