#!/usr/bin/env python3
"""
Telegraf processors.execd script to dynamically add Application version to InfluxDB metrics.

This script:
1. Retrieves the Application version from "dpkg -s <application_name>" every 60 seconds using a background daemon thread.
2. Processes Telegraf metrics from sys.stdin, matching InfluxDB Line Protocol data.
3. Modifies the tags section to include Application version before sending the output to sys.stdout.
4. Handles different metric formats:
    - Custom metrics with tags (measurement,tags fields timestamp)
    - Plugin metrics without tags (measurement fields timestamp)
5. Ensures continuous execution:
    - If parsing fails, prints the original line to avoid breaking the pipeline.
    - Uses sys.stdout.flush() to prevent buffering issues in Telegraf.
"""
import re
import subprocess
import sys
import threading
import time

application_version = ""  # Global variable to store the latest Application version


def get_application_version():
    """Retrieve the installed Application version using dpkg."""
    version = subprocess.run(
        "dpkg -s <application_name> | grep Version | awk '{print $2}'",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()
    return version


def update_application_version():
    """Background thread to periodically update application_version every 60 seconds."""
    global application_version
    while True:
        application_version = get_application_version()
        time.sleep(60)  # Update every 1 minutes


# Start the background daemon thread
threading.Thread(target=update_application_version, daemon=True).start()

# Regex patterns for different InfluxDB metric formats
CUSTOM_METRICS_PATTERN = re.compile(r"(?P<measurement>[^,]+),(?P<tags>(?:\\.|[^ ])+) (?P<fields>.+) (?P<timestamp>\d+)")
PLUGIN_METRICS_PATTERN = re.compile(r"(?P<measurement>[^ ]+) (?P<fields>[^ ]+) (?P<timestamp>\d+)")

# Process incoming metrics from Telegraf
for line in sys.stdin:
    try:
        match = CUSTOM_METRICS_PATTERN.match(line.strip()) or PLUGIN_METRICS_PATTERN.match(line.strip())
        if match and application_version:
            match_dict = match.groupdict()
            measurement = match_dict['measurement']
            tags = match_dict.get('tags')
            fields = match_dict['fields']
            timestamp = match_dict['timestamp']
            tags = f"{tags},application_version={application_version}" if tags else f"application_version={application_version}"
            line = f"{measurement},{tags} {fields} {timestamp}"
    except Exception as e:
        pass
    finally:
        print(line)
        sys.stdout.flush()
