# MicroFaaS
FaaS on small, embedded-system-like compute nodes

## Requirements

* Python 3.7+
  * Adafruit_BBIO

## Fetching Linux 5.11.22 for ARM
```
git clone git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
git remote add stable git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git
git fetch stable
git checkout stable/linux-5.11.y
export CROSS_COMPILE=arm-linux-gnueabihf-
export ARCH=arm
make omap2plus_defconfig
cd linux
mv ../MicroFaaS/linux-patches/bbb.patch ./
patch -fp0 < ../bbb.patch
```
