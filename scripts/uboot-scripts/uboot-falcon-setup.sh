#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Incorrect number of arguments"
    echo "Usage: $0 [WORKER_ID] [TTY_DEVICE]"
    exit
fi

TTY=$2
send() {
    echo $1 
    echo $1 > $TTY
    sleep 0.3
}

send "root"
send "dd if=/root/sdcard.img of=/dev/mmcblk1"
send "sync"
send "poweroff"
echo "Reboot into eMMC system."
echo "Then stop at kernel command line by pressing any key upon boot."
read -p "Press enter to continue."
#send "setenv args_mmc 'setenv bootargs silent quiet reboot=force loglevel=0 lpj=4980736 ip=192.168.1.10::192.168.1.1:255.255.255.0:worker3:eth0:off:1.1.1.1:8.8.8.8:209.50.63.74 console=ttyS0,115200n8 root=/dev/ram0 rootfstype=ramfs rdinit=/sbin/init'"
send "setenv args_mmc 'setenv bootargs quiet loglevel=0 lpj=4980736 ip=192.168.1.${1}::192.168.1.1:255.255.255.0:worker${1}:eth0:off:1.1.1.1:8.8.8.8:209.50.63.74 console=ttyS0,115200n8 root=/dev/ram0 rootfstype=ramfs rdinit=/sbin/init'"
send "mmc dev 1"
send "setenv loadfdt 'mmc dev 1; mmc read \${fdtaddr} 80 180'"
send "setenv loadimage 'mmc read \${loadaddr} 900 3000'"
send "setenv bootcmd 'run args_mmc; run loadfdt; run loadimage;\\"
send "bootm \${loadaddr} - \${fdtaddr}'"
send "saveenv"
send "run args_mmc"
send "run loadimage"
send "run loadfdt"
send "spl export fdt \${loadaddr} - \${fdtaddr}"
send "mmc write \${fdtaddr} 80 180"
send "setenv boot_os 1"
send "saveenv"
send "reset"
