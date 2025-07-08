

import argparse

import config
from utils import multiprocessing

from monitor.promtail.client_promtail import ClientPromtail
from monitor.telegraf.client_telegraf import ClientTelegraf

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true", help="Update only")
    parser.add_argument("--telegraf", action="store_true", help="Install agent telegraf")
    parser.add_argument("--promtail", action="store_true", help="Install agent promtail")
    args = parser.parse_args()

    tasks = []
    for client in config.CLIENTS:
        if args.promtail:
            promtail = ClientPromtail(
                ip=client.ip,
                user=client.ssh_user,
                pwd=client.ssh_pwd,
                ssh_port=client.ssh_port,
                hostname=client.hostname
            )
            if args.update:
                tasks.append(promtail.update)
            else:
                tasks.append(promtail.install)
        if args.telegraf:
            telegraf = ClientTelegraf(
                ip=client.ip,
                user=client.ssh_user,
                pwd=client.ssh_pwd,
                ssh_port=client.ssh_port,
                hostname=client.hostname,
                organization=client.organization,
                bucket=client.bucket
            )
            if args.update:
                tasks.append(telegraf.update)
            else:
                tasks.append(telegraf.install)

    results = list(multiprocessing(tasks))
