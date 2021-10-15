#!/bin/bash
cd ../../../linux-5.11.22
make x86_64_defconfig
patch -fp0 --fuzz 3 --ignore-whitespace < ../MicroFaaS/linux-patches/x86.patch
cd ..
mv linux-5.11.22 linux-minimal
