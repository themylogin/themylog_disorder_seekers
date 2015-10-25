# -*- coding: utf-8 -*-
# crontab(minute="*/10")
# title = "Sentry"
from __future__ import unicode_literals

from django.conf import settings
import isodate
import os
import requests
from requests.auth import HTTPBasicAuth

from themylog.disorder import MaybeDisorder, Disorder as D, maybe_with_title
from themylog.disorder.script import Disorder


if __name__ == "__main__":
    config_file = os.path.expanduser("~/.sentry/sentry.conf.py")
    config = {b"__file__": config_file}
    execfile(config_file, config)
    settings.configure(**{k: v for k, v in config.iteritems()
                          if k in ["DATABASES"] or any(k.startswith("%s_" % s)
                                                       for s in ["AUTH", "SENTRY"])})
    from sentry.models import Project, ProjectKey
    for project in Project.objects.all():
        disorder = Disorder(project.name)
        try:
            key = ProjectKey.objects.get(project=project)
            key.roles.api = True
            key.save()
        except ProjectKey.DoesNotExist:
            continue
        groups = requests.get("http://sentry.thelogin.ru/api/0/projects/%s/%s/groups/?status=unresolved" %
                              (project.slug, project.organization.slug),
                              auth=HTTPBasicAuth(key.public_key, key.secret_key)).json()
        if isinstance(groups, list):
            disorder.fail([maybe_with_title(MaybeDisorder(is_disorder=True,
                                                          disorder=D(datetime=isodate.parse_datetime(group["firstSeen"]),
                                                                     reason=group["title"],
                                                                     data=group)),
                                            group["culprit"])
                           for group in groups])
        else:
            disorder.ok("Нет ошибок")
