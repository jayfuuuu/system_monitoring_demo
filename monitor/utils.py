import concurrent.futures
from typing import Callable, List, Tuple

import paramiko


class SshConnect:
    def __init__(self, ip, user, pwd, port=22):
        self.ip = ip
        self.user = user
        self.pwd = pwd
        self.port = port
        self.__connect()

    def __connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.ip, self.port, self.user, self.pwd)
        self.client.get_transport().set_keepalive(3)

    def send_command(self, command):
        _, stdout, _ = self.client.exec_command(command, timeout=180)
        return stdout.read()

    def get_transport(self):
        return self.client.get_transport()

    def close_connection(self):
        self.client.close()


def multiprocessing(functions: List[Callable], args: List[Tuple] = []):
    args = args if args else [()] * len(functions)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(functions[i], *args[i]) for i in range(len(functions))]
        for future in futures:
            yield future.result()
