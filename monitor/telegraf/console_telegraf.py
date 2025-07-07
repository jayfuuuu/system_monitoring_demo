import os
import socket
from time import sleep

import config
from scp import SCPClient
from utils import SshConnect

FILE_ROOT = os.path.dirname(__file__)

TELEGRAF_SCRIPT = FILE_ROOT + "/telegraf.sh"
TELEGRAF_SCRIPT_TARGET = "/etc/telegraf/telegraf.sh"

TELEGRAF_CONF = FILE_ROOT + "/telegraf.conf"
TELEGRAF_TARGET = "/etc/telegraf/telegraf.conf"

SCRIPT_FOLDER = FILE_ROOT + "/scripts"
SCRIPT_TARGET = "/etc/telegraf"

TELEGRAF_DAEMON_FILE = FILE_ROOT + "/telegraf.service"
TELEGRAF_DAEMON_TARGET = "/etc/systemd/system/telegraf.service"


class ClientTelegraf:

    def __init__(self, ip, user, pwd, hostname, organization, bucket, ssh_port=22):
        self.hostname = hostname
        self.organization = organization
        self.bucket = bucket
        self.ssh_conn = SshConnect(
            ip=ip,
            user=user,
            pwd=pwd,
            port=ssh_port
        )
        core = self.ssh_conn.send_command("uname -m").decode("ascii").strip("\n")
        if core == "x86_64":
            self.DOWNLOAD_TELEGRAF_URL = config.DOWNLOAD_AMD64_TELEGRAF_URL
        else:
            self.DOWNLOAD_TELEGRAF_URL = config.DOWNLOAD_ARM64_TELEGRAF_URL

    def _copy_file_to_console(self, copy_from, copy_to):
        with SCPClient(self.ssh_conn.get_transport()) as scp:
            scp.put(copy_from, copy_to)
            print(f'Copy {copy_from} to {copy_to}')

    def _install_telegraf(self):
        print("Installing Telegraf ...")
        self.ssh_conn.send_command("rm telegraf*")
        self.ssh_conn.send_command("systemctl stop telegraf")
        self.ssh_conn.send_command("rm -r /etc/telegraf")
        self.ssh_conn.send_command("rm -r /etc/default/telegraf")
        self.ssh_conn.send_command(f"wget --no-check-certificate {self.DOWNLOAD_TELEGRAF_URL} -O telegraf_package.deb")
        for _ in range(3):
            self.ssh_conn.send_command("dpkg --force-confmiss -i telegraf_package.deb")
            if self.ssh_conn.send_command("ls /etc | grep -e telegraf"):
                break
            print(f"Retry Install Telegraf: {self.hostname}")
            sleep(3)
        else:
            raise Exception("Install Telegraf Failed")
        self.ssh_conn.send_command("rm telegraf_package.deb")

    def _set_up_telegraf_daemon(self):
        print("Set System Daemon")
        self._copy_file_to_console(TELEGRAF_SCRIPT, TELEGRAF_SCRIPT_TARGET)
        self._copy_file_to_console(TELEGRAF_DAEMON_FILE, TELEGRAF_DAEMON_TARGET)
        self.ssh_conn.send_command(f"perl -pi -e 's|R_INFLUX_TOKEN|{config.INFLUX_TOKEN}|g;' {TELEGRAF_DAEMON_TARGET}")
        self.ssh_conn.send_command(f"perl -pi -e 's|R_ORGANIZATION|{self.organization}|g;' {TELEGRAF_DAEMON_TARGET}")
        self.ssh_conn.send_command(f"perl -pi -e 's|R_BUCKET|{self.bucket}|g;' {TELEGRAF_DAEMON_TARGET}")

        self.ssh_conn.send_command("sudo systemctl daemon-reload")
        self.ssh_conn.send_command("sudo systemctl start telegraf.service")
        self.ssh_conn.send_command("sudo systemctl enable telegraf.service")

    def _set_up_telegraf_config(self):
        print("Setup Telegraf Configuration")
        self._copy_file_to_console(TELEGRAF_CONF, TELEGRAF_TARGET)
        self.ssh_conn.send_command(f"perl -pi -e 's|R_INFLUXDB_URL|{config.INFLUXDB_URL}|g;' {TELEGRAF_TARGET}")
        self.ssh_conn.send_command(f"perl -pi -e 's|R_HOSTNAME|{self.hostname}|g;' {TELEGRAF_TARGET}")

    def _add_additional_scripts(self):
        print('Add Additional Scripts')
        for script in os.listdir(SCRIPT_FOLDER):
            self._copy_file_to_console(f"{SCRIPT_FOLDER}/{script}", SCRIPT_TARGET)
            self.ssh_conn.send_command(f"sudo chmod u+x {SCRIPT_TARGET}/{script}")

    def install(self):
        try:
            self._install_telegraf()
            self.update()
        except socket.timeout as e:
            print(f"Socket Timeout: {e}, {self.hostname}")
        except Exception as e:
            print(f"FAILED: {e}, {self.hostname}")

    def update(self):
        try:
            self._add_additional_scripts()
            self._set_up_telegraf_config()
            self._set_up_telegraf_daemon()
            self.ssh_conn.send_command("sudo systemctl restart telegraf.service")
            self.ssh_conn.close_connection()
        except socket.timeout as e:
            print(f"Socket Timeout: {e}, {self.hostname}")
        except Exception as e:
            print(f"FAILED: {e}, {self.hostname}")
