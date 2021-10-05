#!/bin/sh
# Adapted from https://embexus.com/2017/05/07/fast-boot-linux-with-u-boot-falcon-mode/
dd if=/dev/zero of=sdcard.img bs=1M count=64
dd if=am335x-boneblack.dtb of=sdcard.img bs=1 seek=65536
dd if=MLO of=sdcard.img bs=1 seek=262144
dd if=u-boot.img of=sdcard.img bs=1 seek=393216
dd if=uImage of=sdcard.img bs=1 seek=1179648
