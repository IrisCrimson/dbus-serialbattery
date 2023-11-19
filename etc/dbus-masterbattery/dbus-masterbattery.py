#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Union

from time import sleep
from dbus.mainloop.glib import DBusGMainLoop
from threading import Thread
import sys

if sys.version_info.major == 2:
    import gobject
else:
    from gi.repository import GLib as gobject

# Victron packages
# from ve_utils import exit_on_error

from dbushelper import DbusHelper
from utils import logger
import utils
from battery import Battery
import logging

from bms.master_battery import MasterBattery

logger.info('Starting dbus-battery-master')

def main():

    def poll_battery(loop):
        # Run in separate thread. Pass in the mainloop so the thread can kill us if there is an exception.
        poller = Thread(target=lambda: helper.publish_battery(loop))
        # Thread will die with us if deamon
        poller.daemon = True
        poller.start()
        return True

    logger.info("dbus-battery-master v" + str(utils.DRIVER_VERSION))
    
    battery: Battery = MasterBattery()

    battery.test_connection()
    #os._exit(1)

    battery.log_settings()

    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)
    if sys.version_info.major == 2:
        gobject.threads_init()
    mainloop = gobject.MainLoop()

    # Get the initial values for the battery used by setup_vedbus
    helper = DbusHelper(battery)
    if not helper.setup_vedbus():
        logger.error("ERROR >>> Problem with battery master set up")
        os.exit(1)
    logger.info('Battery master running at dbus')


    # Poll the battery at INTERVAL and run the main loop
    gobject.timeout_add(battery.poll_interval, lambda: poll_battery(mainloop))
    try:
        mainloop.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
