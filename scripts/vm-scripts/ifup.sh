#!/bin/bash

switch=br0

if [ -n "$1" ];then
        ip tuntap add $1 mode tap user `whoami`
        ip link set $1 up
        ip link set $1 master $switch
        exit 0
else
        echo "Error: no interface specified"
        exit 1
fi
