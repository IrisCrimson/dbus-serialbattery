#!/bin/bash

# remove comment for easier troubleshooting
#set -x

# app=$(dirname $0)/dbus-masterbattery.py

python /opt/victronenergy/dbus-masterbattery/dbus-masterbattery.py
