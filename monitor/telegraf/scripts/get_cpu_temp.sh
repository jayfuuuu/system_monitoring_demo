#!/bin/bash
if uname -a | grep -q ui-qcom; then
    echo "cpu_info temp=\"$(cat /sys/class/thermal/thermal_zone0/temp)\" $(date +%s%N)"
else
    echo "cpu_info temp=\"$(sensors | grep temp1 | awk '{print $2}' | grep -oe "[[:digit:]]\+.[[:digit:]]")\" $(date +%s%N)"
fi
