#!/bin/bash

# remove comment for easier troubleshooting
#set -x

# copy config.ini in case it was changed
cp -f /data/etc/dbus-masterbattery/config.ini /opt/victronenergy/dbus-masterbattery/config.ini

# kill driver, if running. It gets restarted by the service daemon
pkill -f "python .*/dbus-masterbattery.py"
