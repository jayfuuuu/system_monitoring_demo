#!/bin/bash

iostat=$(iostat -dxyk 5 1)
if uname -a | grep -q ui-qcom; then
    for i in sda; do
        echo "$iostat" | grep $i | awk '{print $1 " " $4 " " $5 " " $6 " " $7 " " $11 " " $12 " " $9 " " $14}' | tr "," "." | while read device r_iops w_iops r_kbs w_kbs r_await w_await avgrq_size util; do
            echo "iostat,device=$device avgrq_size_total=$avgrq_size $(date +%s%N)"
            echo "iostat,device=$device r_iops=$r_iops $(date +%s%N)"
            echo "iostat,device=$device w_iops=$w_iops $(date +%s%N)"
            echo "iostat,device=$device r_kbs=$r_kbs $(date +%s%N)"
            echo "iostat,device=$device w_kbs=$w_kbs $(date +%s%N)"
            echo "iostat,device=$device r_await=$r_await $(date +%s%N)"
            echo "iostat,device=$device w_await=$w_await $(date +%s%N)"
            echo "iostat,device=$device util_percents=$util $(date +%s%N)"
        done
    done
else
    for i in sda sdb sdc sdd sde sdf sdg sdq sdig md3; do
        echo "$iostat" | grep $i | awk '{print $1 " " $2 " " $3 " " $4 " " $5 " " $10 " " $11 " " $12 " " $16}' | tr "," "." | while read device r_iops w_iops r_kbs w_kbs r_await w_await avgrq_size util; do
            echo "iostat,device=$device avgrq_size_total=$avgrq_size $(date +%s%N)"
            echo "iostat,device=$device r_iops=$r_iops $(date +%s%N)"
            echo "iostat,device=$device w_iops=$w_iops $(date +%s%N)"
            echo "iostat,device=$device r_kbs=$r_kbs $(date +%s%N)"
            echo "iostat,device=$device w_kbs=$w_kbs $(date +%s%N)"
            echo "iostat,device=$device r_await=$r_await $(date +%s%N)"
            echo "iostat,device=$device w_await=$w_await $(date +%s%N)"
            echo "iostat,device=$device util_percents=$util $(date +%s%N)"
        done
    done
fi
