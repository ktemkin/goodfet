# USBTablet.py
#
# Contains class definitions to implement a USB Tablet

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBEndpoint import *

class USBTabletInterface(USBInterface):
    name = "USB tablet interface"

    hid_descriptor = b'\x09\x21\x01\x00\x00\x01\x22\x4a\x00'
    report_descriptor = b'\x05\x01\x09\x01\xa1\x01\x09\x01\xa1\x00\x05\x09\x19\x01\x29\x03\x15\x00\x25\x01\x95\x03\x75\x01\x81\x02\x95\x01\x75\x05\x81\x01\x05\x01\x09\x30\x09\x31\x15\x00\x26\xff\x7f\x35\x00\x46\xff\x7f\x75\x10\x95\x02\x81\x02\x05\x01\x09\x38\x15\x81\x25\x7f\x35\x00\x45\x00\x75\x08\x95\x01\x81\x06\xc0\xc0'

    def __init__(self, verbose=0):
        descriptors = { 
                USB.desc_type_hid    : self.hid_descriptor,
                USB.desc_type_report : self.report_descriptor
        }

        self.endpoint = USBEndpoint(
                3,          # endpoint number
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                10,         # polling interval, see USB 2.0 spec Table 9-13
                self.handle_buffer_available    # handler function
        )

        USBInterface.__init__(
                self,
                0,          # interface number
                0,          # alternate setting
                3,          # interface class
                0,          # subclass
                0,          # protocol
                0,          # string index
                verbose,
                [ self.endpoint ],
                descriptors
        )

        self.x = 0;
        self.y = 0;


    def handle_buffer_available(self):
        
        try:
            x = int(input("x (1-32767)>"))
            y = int(input("y (1-32767)>"))
        except ValueError:
            print("Invalid value!\n")
            return

        try:
            self.send_click(x, y)
        except:
            print("Send error. (Out of range?)\n")


    def send_click(self, x, y):
        self.send_event(x, y, 0, 0)


    def send_event(self, x, y, z, button_state):
        
        #Compose our HID packet...
        data = bytes([ 
            button_state,
            x & 0xFF,
            x >> 8,
            y & 0xFF,
            y >> 8,
            z
        ])

        self.endpoint.send(data)


class USBTabletDevice(USBDevice):
    name = "USB tablet device"

    def __init__(self, maxusb_app, verbose=0):
        config = USBConfiguration(
                1,                                          # index
                "Emulated Tablet",    # string desc
                [ USBTabletInterface() ]                  # interfaces
        )

        USBDevice.__init__(
                self,
                maxusb_app,
                0,                                    # device class
                0,                                    # device subclass
                0,                                    # protocol release number
                64,                                   # max packet size for endpoint 0
                0x610b,                               # vendor id
                0x4653,                               # product id
                0x3412,                               # device revision
                "Assured Information Security",       # manufacturer string
                "HID Tablet"       ,                  # product string
                "S/N12345",                           # serial number string
                [ config ],
                verbose=verbose
        )

