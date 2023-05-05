#!/bin/sh
dos2unix etc/dbus-serialbattery/qml/PageBattery.qml etc/dbus-serialbattery/qml/PageBatteryCellVoltages.qml etc/dbus-serialbattery/installqml.sh
tar -czvf venus-data_qml.tar.gz --mode='a+rwX' etc/dbus-serialbattery/qml/PageBattery.qml etc/dbus-serialbattery/qml/PageBatteryCellVoltages.qml etc/dbus-serialbattery/installqml.sh
