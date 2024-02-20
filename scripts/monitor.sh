#!/bin/bash

hw=$(tr -d '\0' </sys/firmware/devicetree/base/model)
cpu=$(</sys/class/thermal/thermal_zone0/temp)
cpu_freq=$(</sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq)
gpu=$(vcgencmd measure_temp | cut -c 6-)
uptime=$(uptime -p)
free_mem=$(free  -ht | tail -n 1)
mems=( $free_mem )
#load_line=$(top -b -n 1 |grep 'load average:')
#load=( $load_line )

echo "BEGIN"
echo "hardware: $hw"
echo "cpu_temp: $((cpu/1000)) C"
echo "cpu_freq: $((cpu_freq/1000)) Mhz"
echo "gpu_temp: $gpu"
echo "up_time: $uptime"
echo "total_mem: ${mems[1]}"
echo "free_mem: ${mems[3]}"
echo "used_mem: ${mems[2]}"
#echo "load_1: ${load[10]}"
#echo "load_5: ${load[11]}"
#echo "load_15: ${load[12]}"
echo "END"
