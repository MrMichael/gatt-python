import gatt
import time
import threading
import sys

class AnyDeviceManager(gatt.DeviceManager):
    def device_discovered(self, device):
        global dic
        if "iVS101A" in device.alias():
            alias = str(device.alias())
            addr = device.mac_address.upper()
            alias2 = alias.upper()
            if addr[-2:] == alias2[-2:]:
                dic[addr] = alias
                # print(dic)
        elif "iVS101" in device.alias():
            alias = str(device.alias())
            addr = device.mac_address.upper()
            alias2 = alias.upper()
            if addr[-2:] == alias2[-3:-1]:
                dic[addr] = alias
                # print(dic)

def fun_timer():
    global timer
    global count
    count += 1
    if count < 5:
        timer = threading.Timer(1, fun_timer)
        timer.start()
    else:
        manager.stop_discovery()
        manager.stop()
        timer.cancel()

if __name__ == "__main__":
    dic = { }
    count = 0
    manager = AnyDeviceManager(adapter_name='hci0')
    manager.start_discovery()
    timer = threading.Timer(1, fun_timer)
    timer.start()
    manager.run()
    sys.exit(dic)