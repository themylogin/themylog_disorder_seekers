# -*- coding: utf-8 -*-
# crontab(minute="*/30")
# title = "Ethernet-линки"
from __future__ import unicode_literals

import paramiko
import subprocess

from themylog.disorder.script import Disorder


def check_gigabit(disorder, ethtool_output):
    if "\tSpeed: 1000Mb/s" in ethtool_output:
        disorder.ok("Линк 1000Mb/s")
    elif "\tSpeed: 100Mb/s" in ethtool_output:
        disorder.fail("Линк 100Mb/s")
    elif "\tSpeed: 10Mb/s" in ethtool_output:
        disorder.fail("Линк 10Mb/s")
    else:
        disorder.fail("Не удалось разобрать вывод ethtool", ethtool_output=ethtool_output)


if __name__ == "__main__":
    disorder = Disorder("Сервер")
    try:
        server_output = subprocess.check_output(["sudo", "ethtool", "eth0"])
    except:
        disorder.exception("Не удалось запустить ethtool")
    else:
        check_gigabit(disorder, server_output)

    for host, disorder_name, interface in [("192.168.0.3", "Десктоп", "eth0"),
                                           ("192.168.0.4", "Медиацентр", "eth0")]:
        disorder = Disorder(disorder_name)

        try:
            connection = paramiko.SSHClient()
            connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            connection.connect(host, username="themylogin")
        except:
            disorder.exception("Не удалось подключиться к серверу")
        else:
            try:
                stdin, stdout, stderr = connection.exec_command("sudo ethtool %s" % interface)
                output = "".join(stdout.readlines())
            except:
                disorder.exception("Не удалось запустить ethtool")
            else:
                check_gigabit(disorder, output)
