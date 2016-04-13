# -*- coding: utf-8 -*-
# crontab(minute="*/10")
# title = "Sentry"
from __future__ import unicode_literals

import isodate
import os
import requests
from requests.auth import HTTPBasicAuth
import sys

from themylog.disorder import MaybeDisorder, Disorder as D, maybe_with_title
from themylog.disorder.script import Disorder


if __name__ == "__main__":
    url = "http://sentry.thelogin.ru"
    organization = "theloginru"
    auth = HTTPBasicAuth("<api key>", "")

    for team in requests.get("%s/api/0/organizations/%s/teams/" % (url, organization), auth=auth).json():
        for project in sorted(requests.get("%s/api/0/teams/%s/%s/projects/" % (url,
                                                                               organization,
                                                                               team["slug"]),
                                           auth=auth).json(),
                              key=lambda project: project["name"]):
            disorder = Disorder(project["name"])
            groups = requests.get("%s/api/0/projects/%s/%s/groups/?status=unresolved" % (url,
                                                                                         organization,
                                                                                         project["slug"]),
                                  auth=auth).json()
            if groups:
                disorder.fail([maybe_with_title(MaybeDisorder(is_disorder=True,
                                                              disorder=D(datetime=isodate.parse_datetime(group["firstSeen"]),
                                                                         reason=group["title"],
                                                                         data=group)),
                                                group["culprit"])
                               for group in groups])
            else:
                disorder.ok("Нет ошибок")
