#!/bin/bash
#!/bin/bash
cd ../../../linux-5.11.22
make CROSS_COMPILE=arm-linux-gnueabihf- ARCH=arm omap2plus_defconfig
patch -fp0 --fuzz 3 --ignore-whitespace < ../MicroFaaS/linux-patches/bbb.patch
cd ..
mv linux-5.11.22 linux-minimal
