#!/bin/bash
####################################################
## Environment Setup script for MicroFaaS Project ##
## Boston University PEACLAB 2021                 ##
####################################################

sudo apt install -y libssl-dev gcc-arm-linux-gnueabihf bison flex build-essential gcc-arm-linux-gnueabihf u-boot-tools sed make binutils gcc g++ bash patch gzip bzip2 perl tar cpio python unzip rsync wget libncurses-dev

#chmod bobthebuilder.sh
chmod +x bobthebuilder.sh

mkdir ../../projectName
cd ../../projectName
mv ../MicroFaaS .

#Clone linux 5.11.22
#git clone git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
#git remote add stable git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git
#git fetch stable
#git checkout stable/linux-5.11.y
curl -O https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.11.22.tar.xz
tar -xf linux-5.11.22.tar.xz


#Clone linux-initramfs with submodules
git clone --recurse-submodules -j8 git@github.com:peaclab/linux-initramfs.git

