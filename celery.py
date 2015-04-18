# -*- coding: utf-8 -*-
# crontab(minute="*/10")
# title = "Очередь Celery"
from __future__ import unicode_literals

from pytils.numeral import get_plural
import subprocess

from themylog.disorder.script import Disorder


def rabbitmqctl_list(*args):
    return subprocess.check_output(["sudo", "rabbitmqctl"] + list(args)).split("\n")[1:][:-2]


if __name__ == "__main__":
    for vhost in rabbitmqctl_list("list_vhosts")[1:]:
        for queue, tasks in map(lambda s: s.split("\t"), rabbitmqctl_list("list_queues", "-p", vhost)):
            if queue == "celery":
                tasks = int(tasks)
                disorder = Disorder(vhost)
                disorder.state(tasks < 25,
                               "%s в очереди" % get_plural(tasks, ("задача", "задачи", "задач"), "Нет задач"))
