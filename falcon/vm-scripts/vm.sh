#!/bin/bash
if [ $# -ne 1 ]; then
    echo "Incorrect number of arguments"
    echo "Usage: $0 [NUM_VMS]"
    exit
fi
setup (){
echo "Setting up $1 VM's"
	for(( i = 3; i < $1 + 3; i++)); do
	echo "Generating MAC address"
	MAC=$(printf 'DE:AD:BE:EF:00:%02X\n' $((i)))
	echo $MAC
	BOOTARGS=$(printf "\"ip=192.168.1.10%d::192.168.1.1:255.255.255.0:worker%d:eth0:off:1.1.1.1:8.8.8.8:209.50.63.74\"" $((i)) $((i)))
    sudo kvm -M microvm -vga none -nodefaults -no-user-config -nographic -kernel ~/bzImage  -append $BOOTARGS -append "reboot=t root=/dev/ram0 rootfstype=ramfs rdinit=/sbin/init console=ttyS0" -netdev tap,id=net0,script=test/ifup.sh,downscript=test/ifdown.sh    -device virtio-net-device,netdev=net0,mac=$MAC &
done
jobs
}

setup $1

