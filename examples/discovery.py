import gatt
import time
import threading
from argparse import ArgumentParser

class AnyDeviceManager(gatt.DeviceManager):
    def device_discovered(self, device):
        global dic
        # print("[%s] Discovered, alias = %s" % (device.mac_address, device.alias()))
        if "iVS101A" in str(device.alias()):
            alias = str(device.alias())
            addr = device.mac_address.upper()
            alias2 = alias.upper()
            print(addr[-2:], alias2[-2:])
            if addr[-2:] == alias2[-2:]:
                dic[addr] = alias
                print(dic)
        elif "iVS101" in str(device.alias()):
            alias = str(device.alias())
            addr = device.mac_address.upper()
            alias2 = alias.upper()
            print(addr[-2:], alias2[-3:-1])
            if addr[-2:] == alias2[-3:-1]:
                dic[addr] = alias
                print(dic)

def fun_timer():
    global timer
    global count
    count += 1
    if count < int(args.second):
        timer = threading.Timer(1, fun_timer)
        timer.start()
    else:
        fid = open("discovery.log",'w')
        fid.write(str(dic))
        fid.close()
        manager.stop_discovery()
        manager.stop()
        timer.cancel()

if __name__ == "__main__":
    dic = { }
    count = 0
    fid = 0

    arg_parser = ArgumentParser(description="GATT Discovery")
    arg_parser.add_argument('second', help="Scan time")
    args = arg_parser.parse_args()

    if int(args.second) > 30:
        exit("args.second out of range")

    manager = AnyDeviceManager(adapter_name='hci0')
    manager.start_discovery()
    timer = threading.Timer(1, fun_timer)
    timer.start()
    manager.run()
    print(dic)