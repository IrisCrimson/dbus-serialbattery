# -*- coding: utf-8 -*-
from battery import Protection, Battery, Cell
from utils import *
from struct import *
from vedbus import VeDbusService
import dbus

class MasterBattery(Battery):

    BATTERYTYPE = "MasterBattery"

    def __init__(self):
        super(MasterBattery, self).__init__("Master", None, None)
        self.type = self.BATTERYTYPE
        self.cell_count = 0

    def test_connection(self):
        # call a function that will connect to the battery, send a command and retrieve the result.
        # The result or call should be unique to this BMS. Battery name or version, etc.
        # Return True if success, False for failure
        self.get_settings()

        return True

    def get_settings(self):
        # After successful  connection get_settings will be call to set up the battery.
        # Set the current limits, populate cell count, etc
        # Return True if success, False for failure

        # Uncomment if BMS does not supply capacity
        self.capacity = BATTERY_CAPACITY
        self.max_battery_charge_current = MAX_BATTERY_CHARGE_CURRENT
        self.max_battery_discharge_current = MAX_BATTERY_DISCHARGE_CURRENT
        self.hardware_version = self.BATTERYTYPE
        return True

    def refresh_data(self):
        # call all functions that will refresh the battery data.
        # This will be called for every iteration (1 second)
        # Return True if success, False for failure
        result = self.read_soc_data()
        #logger.info("Check data")
        return result

    def extract_alarms(self, system_bus, service, alarm, data_dict):
        if alarm not in data_dict:
            data_dict[alarm] = []
        value = system_bus.get_object(service, "/Alarms/%s"%(alarm)).GetValue()
        if type(value) is not dbus.Array:
            data_dict[alarm].append(value)

    def read_soc_data(self):
        # soc_data = self.read_serial_data_template(self.command_soc)
        # # check if connection success
        # if soc_data is False:
        #     return False
        data_dict = {}

        system_bus = dbus.SystemBus()
        for service in system_bus.list_names():
            if "com.victronenergy.battery." in service and "com.victronenergy.battery.Master" not in service:
                dbus_obj = system_bus.get_object(service, "/ProductName")
                if "SerialBattery" in dbus_obj.GetValue():
                    # print(service)
                    # print("now get the value")
                    # print(dbus_obj)
                    # print(dbus_obj.GetValue())
                    # dbus_obj = system_bus.get_object(service, "/Dc/0")
                    # introspection_interface = dbus.Interface(
                    #     dbus_obj,
                    #     dbus.INTROSPECTABLE_IFACE,)

                    # # Introspectable interfaces define a property 'Introspect' that
                    # # will return an XML string that describes the object's interface
                    # interface = introspection_interface.Introspect()
                    # print(interface)                

                    if "Current" not in data_dict:
                        data_dict["Current"] = []
                    data_dict["Current"].append(system_bus.get_object(service, "/Dc/0/Current").GetValue())

                    if "Voltage" not in data_dict:
                        data_dict["Voltage"] = []
                    data_dict["Voltage"].append(system_bus.get_object(service, "/Dc/0/Voltage").GetValue())

                    if "SOC" not in data_dict:
                        data_dict["SOC"] = []
                    data_dict["SOC"].append(system_bus.get_object(service, "/Soc").GetValue())

                    if "MaxChargeCurrent" not in data_dict:
                        data_dict["MaxChargeCurrent"] = []
                    data_dict["MaxChargeCurrent"].append(system_bus.get_object(service, "/Info/MaxChargeCurrent").GetValue())

                    if "MaxDischargeCurrent" not in data_dict:
                        data_dict["MaxDischargeCurrent"] = []
                    data_dict["MaxDischargeCurrent"].append(system_bus.get_object(service, "/Info/MaxDischargeCurrent").GetValue())

                    if "MaxChargeVoltage" not in data_dict:
                        data_dict["MaxChargeVoltage"] = []
                    data_dict["MaxChargeVoltage"].append(system_bus.get_object(service, "/Info/MaxChargeVoltage").GetValue())

                    if "MaxCellVoltage" not in data_dict:
                        data_dict["MaxCellVoltage"] = []
                    data_dict["MaxCellVoltage"].append(system_bus.get_object(service, "/System/MaxCellVoltage").GetValue())

                    if "MinCellVoltage" not in data_dict:
                        data_dict["MinCellVoltage"] = []
                    data_dict["MinCellVoltage"].append(system_bus.get_object(service, "/System/MinCellVoltage").GetValue())

                    if "CellTemps" not in data_dict:
                        data_dict["CellTemps"] = []
                    data_dict["CellTemps"].append(system_bus.get_object(service, "/System/MaxCellTemperature").GetValue())
                    data_dict["CellTemps"].append(system_bus.get_object(service, "/System/MinCellTemperature").GetValue())

                    if "InstalledCapacity" not in data_dict:
                        data_dict["InstalledCapacity"] = []
                    data_dict["InstalledCapacity"].append(system_bus.get_object(service, "/InstalledCapacity").GetValue())

                    if "capacity" not in data_dict:
                        data_dict["capacity"] = []
                    data_dict["capacity"].append(system_bus.get_object(service, "/Capacity").GetValue())

                    # collect all alarms
                    self.extract_alarms(system_bus, service, "LowVoltage", data_dict)
                    # if "LowVoltage" not in data_dict:
                    #     data_dict["LowVoltage"] = []
                    # value = system_bus.get_object(service, "/Alarms/LowVoltage").GetValue()
                    # if type(value) is not dbus.Array:
                    #     data_dict["LowVoltage"].append(value)

                    self.extract_alarms(system_bus, service, "LowCellVoltage", data_dict)
                    self.extract_alarms(system_bus, service, "HighVoltage", data_dict)
                    self.extract_alarms(system_bus, service, "LowSoc", data_dict)
                    self.extract_alarms(system_bus, service, "HighChargeCurrent", data_dict)
                    self.extract_alarms(system_bus, service, "CellImbalance", data_dict)
                    self.extract_alarms(system_bus, service, "InternalFailure", data_dict)
                    self.extract_alarms(system_bus, service, "LowCellVoltage", data_dict)
                    self.extract_alarms(system_bus, service, "HighChargeTemperature", data_dict)
                    self.extract_alarms(system_bus, service, "LowChargeTemperature", data_dict)
                    self.extract_alarms(system_bus, service, "HighTemperature", data_dict)
                    self.extract_alarms(system_bus, service, "LowTemperature", data_dict)
                    self.extract_alarms(system_bus, service, "BmsCable", data_dict)
                    self.extract_alarms(system_bus, service, "HighInternalTemperature", data_dict)


        voltage, current, soc = 0,0,0 #unpack_from(">hxxhh", soc_data)
        self.voltage = (sum(data_dict["Voltage"])/len(data_dict["Voltage"]))
        #self.voltage = 0
        #print((sum(data_dict["Voltage"])/len(data_dict["Voltage"])))
        self.current = sum(data_dict["Current"])
        self.soc = (sum(data_dict["SOC"])/len(data_dict["SOC"]))

        self.max_battery_charge_current = sum(data_dict["MaxChargeCurrent"])
        #print(data_dict["MaxChargeCurrent"])
        #print(self.max_battery_charge_current)
        self.max_battery_discharge_current = sum(data_dict["MaxDischargeCurrent"])
        #print(self.max_battery_discharge_current)
        self.control_voltage = (sum(data_dict["MaxChargeVoltage"])/len(data_dict["MaxChargeVoltage"]))
        
        self.cell_max_voltage = max(data_dict["MaxCellVoltage"])
        self.cell_min_voltage = max(data_dict["MinCellVoltage"])
        self.to_temp(1, max(data_dict["CellTemps"]))
        self.to_temp(2, min(data_dict["CellTemps"]))
        
        #self.installedcapacity = sum(data_dict["InstalledCapacity"])
        self.capacity = sum(data_dict["InstalledCapacity"])

        self.protection.voltage_low          = max(data_dict["LowVoltage"]) if len(data_dict["LowVoltage"]) > 0 else 0
        self.protection.voltage_cell_low     = max(data_dict["LowCellVoltage"]) if len(data_dict["LowCellVoltage"]) > 0 else 0
        self.protection.voltage_high         = max(data_dict["HighVoltage"]) if len(data_dict["HighVoltage"]) > 0 else 0
        self.protection.soc_low              = max(data_dict["LowSoc"]) if len(data_dict["LowSoc"]) > 0 else 0
        self.protection.current_over         = max(data_dict["HighChargeCurrent"]) if len(data_dict["HighChargeCurrent"]) > 0 else 0
        self.protection.cell_imbalance       = max(data_dict["CellImbalance"]) if len(data_dict["CellImbalance"]) > 0 else 0
        self.protection.internal_failure     = max(data_dict["InternalFailure"]) if len(data_dict["InternalFailure"]) > 0 else 0
        self.protection.temp_high_charge     = max(data_dict["HighChargeTemperature"]) if len(data_dict["HighChargeTemperature"]) > 0 else 0
        self.protection.temp_low_charge      = max(data_dict["LowChargeTemperature"]) if len(data_dict["LowChargeTemperature"]) > 0 else 0
        self.protection.temp_high_discharge         = max(data_dict["HighTemperature"]) if len(data_dict["HighTemperature"]) > 0 else 0
        self.protection.temp_low_discharge          = max(data_dict["LowTemperature"]) if len(data_dict["LowTemperature"]) > 0 else 0
        self.protection.block_because_disconnect    = max(data_dict["BmsCable"]) if len(data_dict["BmsCable"]) > 0 else 0
        self.protection.temp_high_internal          = max(data_dict["HighInternalTemperature"]) if len(data_dict["HighInternalTemperature"]) > 0 else 0

        return True