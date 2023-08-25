#!/usr/bin/env python
from iq_common import apps as apps
from iq_common import saveExcelReport as saveExcelReport


def main():
    saveExcelReport("appReport", apps)


if __name__ == "__main__":
    main()
