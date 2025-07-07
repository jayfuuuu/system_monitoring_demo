# Server Side

This system ([TIG Stacks](https://www.influxdata.com/blog/tig-stack-iiot-ot/) & [Loki](https://grafana.com/docs/loki/latest/)) can collect relevant metrics such as CPU, memory, disk usage, and network I/O from the client. It can also display error logs and response time of key APIs from Application. Additionally, you can add your scripts to monitor more metrics or applications that interest you.

After a period of internal usage, it has helped us to detect potential memory leak issues in the early development stage, and evaluate the results of system optimizations. We believe this tool can provide developers with some help during development and debugging.

Setting up this system is lightweight. We've developed some Python scripts and Docker configurations, so you just need to fill in the necessary parameters in the configuration and execute a few commands to complete the setup.

Hope this tool can be helpful to everyone! The documentation on how to set it up is here. Be sure to fill in the necessary parameters in the configuration and understand the reminders for the setup. If you have any ideas or questions about the system, feel free to share them with us.

## Note
- Please confirm that the `Docker` environment is ready

## Install
1. Update the parameters in `.env` file according to your environment
- Feel free to edit these settings, or just keep the defaults
    - `DOCKER_INFLUXDB_INIT_USERNAME`
    - `DOCKER_INFLUXDB_INIT_PASSWORD`
- ❗️You can change these settings, but please note that they need to be consistent with the two `config.py` files below
    - `DOCKER_INFLUXDB_INIT_ORG`
    - `DOCKER_INFLUXDB_INIT_BUCKET`
    - `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN`
- ❗️ These two parameters related to Grafana template, please changed them together
    - `INFLUXDB_UID`
    - `LOKI_UID`
2. Create containers through docker-compose
```bash
docker compose -f docker-compose.monitor.yaml up -d
```
3. Check if your server started successfully
    - Grafana: `http://{server_ip}:3000`
    - InfluxDB: `http://{server_ip}:8086` 