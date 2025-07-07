from dataclasses import dataclass


@dataclass
class Client:
    ip: str
    ssh_user: str
    ssh_pwd: str
    ssh_port: str
    hostname: str
    organization: str
    bucket: str


SERVER_IP = "<SERVER_IP>"

# Promtail
LOKI_URL = f"http://{SERVER_IP}:3100/loki/api/v1/push"
DOWNLOAD_AMD64_PROMTAIL_URL = "https://github.com/grafana/loki/releases/download/v2.9.4/promtail_2.9.4_amd64.deb"
DOWNLOAD_ARM64_PROMTAIL_URL = "https://github.com/grafana/loki/releases/download/v2.9.4/promtail_2.9.4_arm64.deb"

# Telegraf
DEFAULT_ORGANIZATION = "<ORGANIZATION_NAME>"
DEFAULT_BUCKET = "<BUCKET_NAME>"
INFLUXDB_URL = f"http://{SERVER_IP}:8086"
INFLUX_TOKEN = "<INFLUX_TOKEN>"
DOWNLOAD_AMD64_TELEGRAF_URL = "https://dl.influxdata.com/telegraf/releases/telegraf_1.29.4-1_amd64.deb"
DOWNLOAD_ARM64_TELEGRAF_URL = "https://dl.influxdata.com/telegraf/releases/telegraf_1.29.4-1_arm64.deb"

CLIENTS = [
    Client(
        ip="<CLIENT_IP>",
        ssh_user="<CLIENT_USER>",
        ssh_pwd="<CLIENT_PWD>",
        ssh_port=22,
        hostname="<CLIENT_HOSTNAME>",
        organization=DEFAULT_ORGANIZATION,
        bucket=DEFAULT_BUCKET
    ),
    Client(
        ip="<CLIENT_IP>",
        ssh_user="<CLIENT_USER>",
        ssh_pwd="<CLIENT_PWD>",
        ssh_port=22,
        hostname="<CLIENT_HOSTNAME>",
        organization=DEFAULT_ORGANIZATION,
        bucket=DEFAULT_BUCKET
    ),
]
