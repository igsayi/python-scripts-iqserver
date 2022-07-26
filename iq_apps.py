#!/usr/bin/env python
from iq_common import apps as apps
from iq_common import savecsvreport as savecsvreport


def main():
    savecsvreport("appReport", apps)


if __name__ == "__main__":
    main()
