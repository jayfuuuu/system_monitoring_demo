import os
import socket
from time import sleep

import config
from scp import SCPClient
from utils import SshConnect

FILE_ROOT = os.path.dirname(__file__)

PROMTAIL_SCRIPT = FILE_ROOT + "/promtail.sh"
PROMTAIL_SCRIPT_TARGET = "/etc/promtail/promtail.sh"

PROMTAIL_CONF = FILE_ROOT + "/config.yml"
PROMTAIL_CONF_TARGET = "/etc/promtail/config.yml"

PROMTAIL_DAEMON_FILE = FILE_ROOT + "/promtail.service"
PROMTAIL_DAEMON_TARGET = "/etc/systemd/system/promtail.service"


class ClientPromtail:

    def __init__(self, ip, user, pwd, hostname, ssh_port=22):
        self.hostname = hostname
        self.ssh_conn = SshConnect(
            ip=ip,
            user=user,
            pwd=pwd,
            port=ssh_port
        )
        self.core = self.ssh_conn.send_command("uname -m").decode("ascii").strip("\n")
        if self.core == "x86_64":
            self.DOWNLOAD_PROMTAIL_URL = config.DOWNLOAD_AMD64_PROMTAIL_URL
        else:
            self.DOWNLOAD_PROMTAIL_URL = config.DOWNLOAD_ARM64_PROMTAIL_URL

    def _copy_file_to_console(self, copy_from, copy_to):
        with SCPClient(self.ssh_conn.get_transport()) as scp:
            scp.put(copy_from, copy_to)
            print(f'Copy {copy_from} to {copy_to}')

    def _install_promtail(self):
        print("Installing Promtail ...")
        self.ssh_conn.send_command("rm promtail*")
        self.ssh_conn.send_command("systemctl stop promtail")
        self.ssh_conn.send_command("rm -r /etc/promtail")
        self.ssh_conn.send_command(f"wget --no-check-certificate {self.DOWNLOAD_PROMTAIL_URL} -O promtail_package.deb")
        for _ in range(3):
            self.ssh_conn.send_command("dpkg --force-confmiss -i promtail_package.deb")
            if self.ssh_conn.send_command("ls /etc | grep -e promtail"):
                break
            print(f"Retry Install Promtail: {self.hostname}")
            sleep(3)
        else:
            raise Exception("Install Promtail Failed")
        self.ssh_conn.send_command("rm promtail_package.deb")

    def _set_up_promtail_daemon(self):
        print("Set System Daemon")
        self._copy_file_to_console(PROMTAIL_SCRIPT, PROMTAIL_SCRIPT_TARGET)
        self._copy_file_to_console(PROMTAIL_DAEMON_FILE, PROMTAIL_DAEMON_TARGET)
        self.ssh_conn.send_command("sudo systemctl daemon-reload")
        self.ssh_conn.send_command("sudo systemctl start promtail.service")
        self.ssh_conn.send_command("sudo systemctl enable promtail.service")

    def _set_up_promtail_config(self):
        print("Setup Promtail Configuration")
        self._copy_file_to_console(PROMTAIL_CONF, PROMTAIL_CONF_TARGET)
        self.ssh_conn.send_command(f"perl -pi -e 's|R_LOKI_URL|{config.LOKI_URL}|g;' {PROMTAIL_CONF_TARGET}")
        self.ssh_conn.send_command(f"perl -pi -e 's|R_HOSTNAME|{self.hostname}|g;' {PROMTAIL_CONF_TARGET}")

    def install(self):
        try:
            self._install_promtail()
            self.update()
        except socket.timeout as e:
            print(f"Socket Timeout: {e}, {self.hostname}")
        except Exception as e:
            print(f"FAILED: {e}, {self.hostname}")

    def update(self):
        try:
            self._set_up_promtail_config()
            self._set_up_promtail_daemon()
            self.ssh_conn.send_command("sudo systemctl restart promtail.service")
            self.ssh_conn.close_connection()
        except socket.timeout as e:
            print(f"Socket Timeout: {e}, {self.hostname}")
        except Exception as e:
            print(f"FAILED: {e}, {self.hostname}")
