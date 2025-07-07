#!/bin/bash
bad_disk=0
for i in /dev/sd[a-g]; do
    dev=`echo "$i" | cut -d'/' -f3`
    smartctl=`smartctl -a "$i"`
    smart_test_result=`echo "$smartctl" | grep health | cut -d' ' -f6`
    if [ "$smart_test_result" = "PASSED" ]; then
        echo "smartctl,device=$dev test_result=$((0))"
    elif [ "$smart_test_result" = "FAILED!" ]; then 
        echo "smartctl,device=$dev test_result=$((2))"
        bad_disk=$((bad_disk+1))
    else
        echo "smartctl,device=$dev test_result=$((1))"
        bad_disk=$((bad_disk+1))
    fi
    smartctl_attributes=`echo "$smartctl" | sed -n '/Raw_Read/,/^$/p'`
    if [ -z "$smartctl_attributes" ]; then
        smartctl_attributes=`echo "$smartctl" | sed -n '/Power_On_Hours/,/^$/p'`
    fi
    smartctl_attributes_num=`echo "$smartctl_attributes" | wc -l`
    good_count=0
    in_the_past_count=0
    fail_count=0
    unknown_count=0
    index=0
    echo "$smartctl_attributes" | awk '{print $2 " " $9}' | tr "," "." | while read attr status; do
        index=$((index+1))
        if [ "$status" = "-" ]; then 
            echo "smartctl,attributes=$attr,device=$dev status=$((0))"
            echo "smartctl,attributes=$attr,device=$dev status_str="\""GOOD"\"""
            good_count=$((good_count+1))
        elif [ "$status" = "In_the_past" ]; then 
            echo "smartctl,attributes=$attr,device=$dev status=$((1))"
            echo "smartctl,attributes=$attr,device=$dev status_str="\""$status"\"""
            in_the_past_count=$((in_the_past_count+1))
        elif [ "$status" = "FAILING_NOW" ]; then 
            echo "smartctl,attributes=$attr,device=$dev status=$((2))"
            echo "smartctl,attributes=$attr,device=$dev status_str="\""$status"\"""
            fail_count=$((fail_count+1))
        else
            echo "smartctl,attributes=$attr,device=$dev status=$((3))"
            echo "smartctl,attributes=$attr,device=$dev status_str="\""$status"\"""
            unknown_count=$((unknown_count+1))
        fi
        if [ $index = $smartctl_attributes_num ]; then
            echo "smartctl,device=$dev,attributes_status=good count=$good_count"
            echo "smartctl,device=$dev,attributes_status=fail_in_past count=$in_the_past_count"
            echo "smartctl,device=$dev,attributes_status=failling_now count=$fail_count"
            echo "smartctl,device=$dev,attributes_status=unknown count=$unknown_count"
        fi
    done
    power_on_time=`echo "$smartctl_attributes" | grep Power_On_Hours | awk '{print $10}' | cut -d 'h' -f1`
    echo "smartctl,device=$dev power_on_time=$power_on_time"
done
echo "smartctl error_disks_count=$bad_disk"