#!/bin/bash

# remove comment for easier troubleshooting
#set -x


# check if minimum required Venus OS is installed | start
versionRequired="v2.90"

# elaborate version string for better comparing
# https://github.com/kwindrem/SetupHelper/blob/ebaa65fcf23e2bea6797f99c1c41174143c1153c/updateFileSets#L56-L81
function versionStringToNumber ()
{
    local p4="" ; local p5="" ; local p5=""
    local major=""; local minor=""

	# first character should be 'v' so first awk parameter will be empty and is not prited into the read command
	#
	# version number formats: v2.40, v2.40~6, v2.40-large-7, v2.40~6-large-7
	# so we must adjust how we use paramters read from the version string
	# and parsed by awk
	# if no beta make sure release is greater than any beta (i.e., a beta portion of 999)

    read major minor p4 p5 p6 <<< $(echo $1 | awk -v FS='[v.~-]' '{print $2, $3, $4, $5, $6}')
	((versionNumber = major * 1000000000 + minor * 1000000))
	if [ -z $p4 ] || [ $p4 = "large" ]; then
        ((versionNumber += 999))
	else
		((versionNumber += p4))
    fi
	if [ ! -z $p4 ] && [ $p4 = "large" ]; then
		((versionNumber += p5 * 1000))
		large=$p5
	elif [ ! -z $p6 ]; then
		((versionNumber += p6 * 1000))
	fi
}

# get current Venus OS version
versionStringToNumber "$(head -n 1 /opt/victronenergy/version)"
venusVersionNumber="$versionNumber"

# minimum required version to install the driver
versionStringToNumber "$versionRequired"

if (( $venusVersionNumber < $versionNumber )); then
    echo
    echo
    echo "Minimum required Venus OS version \"$versionRequired\" not met. Currently version \"$(head -n 1 /opt/victronenergy/version)\" is installed."
    echo
    echo "Please update via \"Remote Console/GUI -> Settings -> Firmware -> Online Update\""
    echo "OR"
    echo "by executing \"/opt/victronenergy/swupdate-scripts/check-updates.sh -update -force\""
    echo
    echo "Install the driver again after Venus OS was updated."
    echo
    echo
    exit 1
fi
# check if minimum required Venus OS is installed | end


# handle read only mounts
bash /opt/victronenergy/swupdate-scripts/remount-rw.sh

# install
rm -rf /opt/victronenergy/service/dbus-masterbattery
rm -rf /opt/victronenergy/service-templates/dbus-masterbattery
rm -rf /opt/victronenergy/dbus-masterbattery
mkdir /opt/victronenergy/dbus-masterbattery
mkdir /opt/victronenergy/dbus-masterbattery/bms
cp -f /data/etc/dbus-masterbattery/* /opt/victronenergy/dbus-masterbattery &>/dev/null
cp -f /data/etc/dbus-masterbattery/bms/* /opt/victronenergy/dbus-masterbattery/bms &>/dev/null
cp -rf /data/etc/dbus-masterbattery/service /opt/victronenergy/service-templates/dbus-masterbattery

# add install-script to rc.local to be ready for firmware update
filename=/data/rc.local
if [ ! -f "$filename" ]; then
    echo "#!/bin/bash" > "$filename"
    chmod 755 "$filename"
fi
grep -qxF "bash /data/etc/dbus-masterbattery/reinstall-local.sh" $filename || echo "bash /data/etc/dbus-masterbattery/reinstall-local.sh" >> $filename

# add empty config.ini, if it does not exist to make it easier for users to add custom settings
filename="/data/etc/dbus-masterbattery/config.ini"
if [ ! -f "$filename" ]; then
    {
        echo "[DEFAULT]"
        echo
        echo "; If you want to add custom values/settings, then check the values/settings you want to change in \"config.default.ini\""
        echo "; and insert them below to persist future driver updates."
        echo
        echo "; Example (remove the semicolon \";\" to uncomment and activate the value/setting):"
        echo "; MAX_BATTERY_CHARGE_CURRENT = 50.0"
        echo "; MAX_BATTERY_DISCHARGE_CURRENT = 60.0"
        echo
        echo
    } > $filename
fi

# kill driver, if running. It gets restarted by the service daemon
pkill -f "supervise dbus-masterbattery*"
pkill -f "multilog .* /var/log/dbus-masterbattery*"
pkill -f "python .*/dbus-masterbattery.py*"


### START ###

# stop all dbus-masterbattery services, if at least one exists
if [ -d "/service/dbus-masterbattery" ]; then
    svc -u /service/dbus-masterbattery*

    # always remove existing canbattery services to cleanup
    rm -rf /service/dbus-masterbattery*

    # kill all masterbattery processes that remain
    pkill -f "supervise dbus-masterbattery*"
    pkill -f "multilog .* /var/log/dbus-masterbattery*"
    pkill -f "python .*/dbus-masterbattery.py *"
fi

# install required packages
# TO DO: Check first if packages are already installed
echo "Installing required packages to start master battery..."

opkg update
opkg install python3-misc python3-pip

echo "done."
echo

# function to install master battery
install_masterbattery_service() {
    echo "Installing Master Battery"

    mkdir -p "/service/dbus-masterbattery/log"
    {
        echo "#!/bin/sh"
        echo "exec multilog t s25000 n4 /var/log/dbus-masterbattery"
    } > "/service/dbus-masterbattery/log/run"
    chmod 755 "/service/dbus-masterbattery/log/run"

    {
        echo "#!/bin/sh"
        echo "exec 2>&1"
        echo "echo"
        echo "python /opt/victronenergy/dbus-masterbattery/dbus-masterbattery.py"
    } > "/service/dbus-masterbattery/run"
    chmod 755 "/service/dbus-masterbattery/run"
}

install_masterbattery_service

### END ###

# install notes
echo
echo
echo "#################"
echo "# Install notes #"
echo "#################"
echo
echo "The installation is complete. You don't have to do anything more."
echo
echo "CUSTOM SETTINGS: If you want to add custom settings, then check the settings you want to change in \"/data/etc/dbus-masterbattery/config.default.ini\""
echo "                 and add them to \"/data/etc/dbus-masterbattery/config.ini\" to persist future driver updates."
echo
echo
