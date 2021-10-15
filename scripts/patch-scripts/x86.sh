#!/bin/bash
cd ../../../linux-minimal
make x86_64_defconfig
patch -fp0 < ../MicroFaas/linux-patches/x86.patch
