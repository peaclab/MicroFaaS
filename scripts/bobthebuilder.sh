#!/bin/bash
DIR=$PWD/../..

make-image () {
cd $DIR/linux-initramfs
mkdir $DIR/.tmp-initramfs
mv .git $DIR/.tmp-initramfs
mv .gitmodules $DIR/.tmp-initramfs

cd $DIR/linux-minimal
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- -j 20 uImage LOADADDR=80008000
mv arch/arm/boot/uImage $DIR/MicroFaaS/scripts/uboot-scripts
cd $DIR/MicroFaaS/scripts/uboot-scripts
/bin/bash $DIR/MicroFaaS/scripts/uboot-scripts/build-falcon-image.sh
mv sdcard.img ../
rm uImage

cd $DIR/linux-initramfs
mv $DIR/.tmp-initramfs/.git .git
mv $DIR/.tmp-initramfs/.gitmodules .gitmodules

rm -rf $DIR/.tmp-initramfs
}

copy_image () {
	echo "Copying sdcard.img to root"
	sudo cp $DIR/MicroFaaS/scripts/sdcard.img /media/$USER/rootfs/root/
	umount /media/$USER/boot
	umount /media/$USER/rootfs
	read -p "Plug SD card into BBB and boot into system. Press enter to continue."
}

copy_image_to_sd () {
if [ -d /media/${USER}/rootfs/root ]; then
	copy_image
else	
	echo "rootfs not found on SD card. "
	read -n 1 -s -r -p "Press enter to burn a new image, or R to refresh." key
	if [ "$key" = "r" ]; then
	echo
	option3
	fi
	echo
	echo
	ls /dev/sd*
	read -p "ID of SD card (i.e sda): " sd_path
	echo "Burning card"
	sudo dd if=$DIR/MicroFaaS/scripts/uboot-scripts/basesys.img of=/dev/$sd_path status=progress
	echo "Remount SD card"
	copy_image_to_sd
		
fi
}

option1 () {
            make-image
            copy_image_to_sd
            echo
            echo
            ls /dev/ttyUSB*
            read -ep "ID of ttyUSB (i.e 0 or 1): " tty
            read -ep "Worker ID: " id
            sudo /bin/bash $DIR/MicroFaaS/scripts/uboot-scripts/uboot-falcon-setup.sh $id /dev/ttyUSB$tty
            echo "Done"
            exit
}

option2 () {
	make-image
}

option3 () {
            copy_image_to_sd
            echo
            echo
            ls /dev/ttyUSB*
            read -ep "ID of ttyUSB (i.e 0 or 1): " tty
            read -ep "Worker ID: " id
            sudo /bin/bash $DIR/MicroFaaS/scripts/uboot-scripts/uboot-falcon-setup.sh "$id" "/dev/ttyUSB$tty"
            echo "Done"
            exit
}

option4() {
	    ls /dev/ttyUSB*
            read -ep "ID of ttyUSB (i.e 0 or 1): " tty
            read -ep "Worker ID: " id
            echo "$tty"
            echo "$id"
            sudo /bin/bash $DIR/MicroFaaS/scripts/uboot-scripts/uboot-falcon-setup.sh "${id}" "/dev/ttyUSB${tty}"
}


PS3='Insert SD card. Please enter your choice: '
options=("Make and copy to SD" "Make sdcard.img only" "Copy to SD" "uBoot script" "Pull all files from GitHub" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "Make and copy to SD")
	    option1
            ;;
        "Make sdcard.img only")
            option2
            ;;
        "Copy to SD")
            option3
            ;;
        "uBoot script")
            option4
            ;;
        "Quit")
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done

