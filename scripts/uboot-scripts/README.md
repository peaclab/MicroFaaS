# Falcon
These scripts are used to setup falcon boot on the beaglebone black. It flashes a device tree binary, uboot image, MLO, and a custom kernel uImage that you create. Once all files are in the directory, running the following command builds a sdcaard.img for falcon boot.
```
./build-falcon-image.sh
```
The dtb for your kernel may vary and need to be rebuilt.

#Booting into Falcon Image
Once the image has been built, place it in the rootfs of your normal kernel. A fresh kernel image is provided in this folder called basesys.img. Flash it on an sd card with balena and add the sdcard.img in root. Once booted up, run the following command to place the sdcard.img in the onboard emmc.
```
dd if=/root/sdcard.img of=/dev/mmcblk1
```
Then reboot into the onboard emmc and enter the uboot prompt by clicking any key upon boot. Run the following command with a worker id and the device file/COM port.

```
./uboot-falcon-setup.sh {workerId} {Device file/COM port}
```
You may encounter an error called Bad Magic or Bad CRC. This may mean that the bootloader is not copying enough blocks for the kernel image. You can fix this by editing the last number in the line: setenv loadimage 'mmc read \${loadaddr} 900 5500' to be a larger number
