# -*- coding: utf-8 -*-
# crontab(minute="*/5")
# title = "Камеры"
from __future__ import unicode_literals

from themylog.disorder.script import Disorder


if __name__ == "__main__":
    syslog = open("/var/log/syslog").read()
    for thread, title in [(1, "Камера в подъезде"),
                          (2, "Камера в отсечке")]:
        disorder = Disorder(title)
        fail_index = syslog.rfind("[%d] Retrying until successful connection with camera" % thread)
        success_index = syslog.rfind("[%d] cap.driver" % thread)
        if success_index >= fail_index:
            disorder.ok("Работает")
        else:
            disorder.fail("Не работает")
