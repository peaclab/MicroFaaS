# Falcon
These scripts are used to setup [falcon boot](https://github.com/u-boot/u-boot/blob/master/doc/README.falcon) on the Beaglebone Black. It flashes a device tree binary, uboot image, MLO, and a custom kernel uImage that you create. Once all files are in the directory, running the following command builds a sdcaard.img for falcon boot.
```
./build-falcon-image.sh
```
The dtb for your kernel may vary and need to be rebuilt.

## Booting into Falcon Image
Once the image has been built, you'll need to flash it onto the eMMC of the Beaglebone. We do this by booting up an SD card containing a temporary OS that is solely used for dd-ing the generated image onto the eMMC. If you'd like to take the same approach, flash `basesys.img` to an SD card with a tool such as [Balena Etcher](https://www.balena.io/etcher/), remount the SD card, and then copy your previously-generated `sdcard.img` onto the root of the SD card. Boot your BeagleBone into the SD card, then run the following command to place the sdcard.img in the onboard emmc.
```
dd if=/sdcard.img of=/dev/mmcblk1
```
Then reboot into the onboard eMMC and enter the uboot prompt by pressing any key upon boot. Run the following command with a worker ID number (any positive integer between 1 and 255) and the device file/COM port.

```
./uboot-falcon-setup.sh {workerId} {Device file/COM port}
```
You may encounter an error called Bad Magic or Bad CRC. This may mean that the bootloader is not copying enough blocks for the kernel image. You can fix this by editing the last number in the line `setenv loadimage 'mmc read \${loadaddr} 900 5500'` to be a larger number.
