#!/bin/bash

# remove comment for easier troubleshooting
#set -x

#stop gui
svc -d /service/gui
#sleep 1 sec
sleep 1
#start gui
svc -u /service/gui
