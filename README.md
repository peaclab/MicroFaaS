# MicroFaaS
FaaS on small, embedded-system-like compute nodes

## Requirements

* Python 3.7+
  * Adafruit_BBIO

## Setting up the MicroFaaS environment
```
clone latest repo
cd MicroFaaS
bash scripts/setupenvironment.sh
```
This will move your current MicroFaaS directory into a larger project folder with the 5.11.22 Linux OS and initramfs

## Patching Linux OS for Optimized Boot Time
```
For ARM based BeagleBoneBlack:
bash projectName/MicroFaaS/scripts/patch-scripts/bbb-arm.sh

For X86 based Rack Server:
bash projectName/MicroFaaS/scripts/patch-scripts/x86.sh
```

## Building and Flashing Minimal Linux OS on BeagleBoneBlack
```
bash projectName/MicroFaaS/scripts/bobthebuilder.sh
```
