# Client Side
- Automatically install and configure telegraf and promtail on your Client

## Install
1. Install the requirement package in your `Python` environment

```bash
pip install -r requirements.txt
```

2. Update the parameters in `/monitor/config.py` file according to your environment.
- `SERVER_IP`
  - Your InfluxDB/Loki server IP
- `ip`, `ssh_user`, `ssh_password`, `ssh_port`, `hostname`
  - Your Client IP and SSH connection
- `DEFAULT_ORGANIZATION`, `DEFAULT_BUCKET`, `INFLUX_TOKEN`
  - Should be consistent with the `.env` file above


3. Execute command

```bash
$ python3 ./monitor/installer.py --telegraf --promtail
```

- If you only want to install one of them
```bash
$ python3 ./monitor/installer.py --telegraf
$ python3 ./monitor/installer.py --promtail
```

4. If you just want to update the config without reinstalling, execute:
```bash
python3 ./monitor/installer.py --telegraf --promtail --update
```
- If you only want to update one of them
```bash
$ python3 ./monitor/installer.py --telegraf --update
$ python3 ./monitor/installer.py --promtail --update
```

5. 🎉 Confirm on the Dashboard whether data has started to be collected