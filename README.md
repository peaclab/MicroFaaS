# MicroFaaS
FaaS on small, embedded-system-like compute nodes

## Requirements

* Python 3.7+
  * Adafruit_BBIO
## Hardware Setup
1. Set up a managed switch with gateway address set to a machine with a DHCP server running with the 192.168.1.x IP range.
2. Connect all 'worker' Beaglebones into the switch. Connect an 'orchestrator' Beaglebone.
3. To measure power consumption, plug managed switch and all Beaglebones into a powerstrip. Connect the powerstrip into a power logging device like the WattsUp Pro.

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

## Building and Flashing Minimal Linux OS on Beaglebone Black Worker
```
bash projectName/MicroFaaS/scripts/bobthebuilder.sh
```
Run option 1 to compile the kernel and start the process for flashing on to the Beaglebone Black. The script will prompt for a microSD card. If the microSD card does not contain a bootable kernel, the script will install one and copy the compiled kernel image to the rootfs. Unmount and insert the microSD card into a powered-off Beaglebone. Connect the Beaglebone using a serial cable (USB-to-TTL), find the device port (typically `/dev/ttyUSB0` or `/dev/ttyUSB1`), then connect via a serial console (i.e. picocom). To boot into the OS installed on the microSD, press and hold the button next to the microSD card port while plugging in the Beaglebone. At the login prompt, return to the script and press Enter to continue which will flash the optimized kernel containing the initramfs onto the onboard eMMC. The script will shutdown the Beaglebone. Power it back on by pressing the power button and hit the spacebar to stop at the kernel command line. Enter the worker id to be used in the local network. Continue by pressing enter, and the script will set up the UBoot falcon mode and reboot. **Make sure the Beaglebone is connected to the switch or it will hang during the boot process as kernel space networking will not be able to connect.**
