#!/bin/bash

# remove comment for easier troubleshooting
#set -x

# disable driver
bash /data/etc/dbus-masterbattery/disable.sh


# remove files in Victron directory. Don't use variables here,
# since on an error the whole /opt/victronenergy gets deleted
rm -rf /opt/victronenergy/service/dbus-masterbattery
rm -rf /opt/victronenergy/service-templates/dbus-masterbattery
rm -rf /opt/victronenergy/dbus-masterbattery


# restore GUI changes
/data/etc/dbus-masterbattery/restore-gui.sh


# uninstall modules
read -r -p "Do you want to uninstall bleak, python3-pip and python3-modules? If you don't know just press enter. [y/N] " response
echo
response=${response,,} # tolower
if [[ $response =~ ^(y) ]]; then
    echo "Uninstalling modules..."
    pip3 uninstall bleak
    opkg remove python3-pip python3-modules
    echo "done."
    echo
fi


read -r -p "Do you want to delete the install and configuration files in \"/data/etc/dbus-masterbattery\"? If you don't know just press enter. [y/N] " response
echo
response=${response,,} # tolower
if [[ $response =~ ^(y) ]]; then
    rm -rf /data/etc/dbus-masterbattery
    echo "The folder \"/data/etc/dbus-masterbattery\" was removed."
    echo
fi


echo "The dbus-masterbattery driver was uninstalled. Please reboot."
echo
