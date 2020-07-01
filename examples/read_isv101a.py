import gatt
import codecs
import sys

from argparse import ArgumentParser

class AnyDevice(gatt.Device):

    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))
        fid = open(args.path,'w')
        fid.write("connect_failed")
        fid.close()
        sys.exit("connect_failed") 

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))
        self.manager.stop()


    def services_resolved(self):
        super().services_resolved()

        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))

        device_information_service = next(
            s for s in self.services
            if s.uuid == '6e400001-b5a3-f393-e0a9-e50e24dcca9e')

        uart_rx_characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == '6e400002-b5a3-f393-e0a9-e50e24dcca9e')

        uart_tx_characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == '6e400003-b5a3-f393-e0a9-e50e24dcca9e')

        # hexstring = b'\xFF\xFF\xFF\xFF\xFF\x0F\x01\x0C\x01\x01\x01\x02\x00\x02\x00\x02\x00\x0F\x00\x00\x0E'
        # hexstring = b'\xFF\xFF\xFF\xFF\xFF\x0E\x08\x0B\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x0C'
        datahex = bytes.fromhex(args.cmd)
        print("args.cmd:", datahex.hex())
        uart_rx_characteristic.write_value(datahex)
        uart_tx_characteristic.enable_notifications(True)

    def characteristic_write_value_succeeded(self, characteristic):
        print("characteristic_write_value_succeeded")

    def characteristic_write_value_failed(self, characteristic, error):
        # print("characteristic_write_value_failed")
        fid = open(args.path,'w')
        fid.write("characteristic_write_value_failed")
        fid.close()
        # sys.exit("characteristic_write_value_failed") 
        device.disconnect()
        manager.stop()

    def characteristic_value_updated(self, characteristic, value):
        if characteristic.uuid == '6e400003-b5a3-f393-e0a9-e50e24dcca9e' :
            global buffflag
            global bufflen
            global count
            global fid

            print("uart_tx:", value.hex())
            if value[0]==0xff and value[1]==0xff and value[2]==0xff :
                buffflag = True
                bufflen = value[9]*0x100 + value[10]
                print("bufflen:",bufflen)
                fid = open(args.path,'w')
                fid.write('')
                fid.close()
                fid = open(args.path,'a')
            if buffflag == True:
                fid.write(value.hex())
                count += len(value)
                print("read sum:",count)
            if count > bufflen+9:
                buffflag = False
                fid.close()
                device.disconnect()
                manager.stop()
            
    def characteristic_enable_notifications_succeeded(self, characteristic):
        print("characteristic_enable_notifications_succeeded")

    
if __name__ == "__main__":
    buffflag = False
    bufflen = 0
    count = 0
    fid = 0

    arg_parser = ArgumentParser(description="GATT Read Characteristic")
    arg_parser.add_argument('mac_address', help="MAC address of device to connect")
    arg_parser.add_argument('cmd', help="CMD data for uart_rx_characteristic")
    arg_parser.add_argument('path', help="File path for recieve data")
    args = arg_parser.parse_args()

    if len(args.mac_address) != 17:
        sys.exit("mac address error") 

    if len(args.cmd)%2 != 0:
        sys.exit("cmd error") 

    manager = gatt.DeviceManager(adapter_name='hci0')

    device = AnyDevice(manager=manager, mac_address=args.mac_address)
    device.connect()

    manager.run()