#!/bin/bash

# remove comment for easier troubleshooting
#set -x

# handle read only mounts
bash /opt/victronenergy/swupdate-scripts/remount-rw.sh

# remove services
rm -rf /service/dbus-masterbattery*

# kill driver, if running
# master battery
pkill -f "supervise dbus-masterbattery*"
pkill -f "multilog .* /var/log/dbus-masterbattery*"
pkill -f "python .*/dbus-masterbattery.py*"

# remove install script from rc.local
sed -i "/bash \/data\/etc\/dbus-masterbattery\/reinstall-local.sh/d" /data/rc.local


echo "The dbus-masterbattery driver was disabled".
echo
