#!/bin/bash

setup (){
echo "Setting up bridge to static IP 192.168.1.201"
ip link add br0 type bridge
ip addr flush dev $ETH
ip link set dev br0 up
ip link set dev $ETH master br0
ifconfig br0 up
dhclient -v br0
echo "Changing bridge IP to 192.168.1.201"
ifconfig br0 192.168.1.201 netmask 255.255.255.0
}

teardown(){
echo "Tearing down tap networking"
ip link del br0
}

while [[ "$1" =~ ^- && ! "$1" == "--" ]]; do case $1 in
  -n | --new )
    shift; ETH=$1
    setup $ETH
    exit
    ;;
  -d | --down )
    shift; ETH=$1
    teardown $ETH
    ;;
  -h | --help )
    echo "setup.sh options:"
    echo "   -n: set up new bridge device with static IP 192.168.1.201. Run using sudo bash setup.sh --new [network device]"
    echo "   -d: take down bridge device. Run using sudo bash setup.sh --down [network device]"
    ;;
esac; shift; done
if [[ "$1" == '--' ]]; then shift; fi
