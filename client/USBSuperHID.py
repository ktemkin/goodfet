# USBTablet.py
#
# Contains class definitions to implement a USB Tablet

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBEndpoint import *


class USBHIDClass(USBClass):
    name = "USB HID device"

    def setup_request_handlers(self):
        self.request_handlers = {
            0x01 : self.handle_finger_count_request,
        }

    def handle_finger_count_request(self, req):
        self.interface.configuration.device.send_control_message(b'\x10\x08')



class USBSuperHIDInterface(USBInterface):
    name = "USB tablet interface"

    hid_descriptor = b'\x09\x21\x01\x01\x00\x01\x22\x54\x00'
    report_descriptor = b'\x05\x0D\x09\x04\xA1\x01\x85\x04\x09\x22\xA1\x00\x09\x42\x15\x00\x25\x01\x75\x01\x95\x01\x81\x02\x09\x32\x81\x02\x09\x37\x81\x02\x25\x1F\x75\x05\x09\x51\x81\x02\x05\x01\x55\x0E\x65\x11\x35\x00\x75\x10\x46\x56\x0A\x26\xFF\x0F\x09\x30\x81\x02\x46\xB2\x05\x26\xFF\x0F\x09\x31\x81\x02\x05\x0D\x75\x08\x85\x10\x09\x55\x25\x10\xB1\x02\xC0\xC0'



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

        self.device_class = USBHIDClass()
        self.device_class.set_interface(self)

        self.x = 0;
        self.y = 0;



    def handle_buffer_available(self):
        self.x = (self.x + 1) % 1458
        self.y = (self.y + 1) % 1458
        
        self.send_finger(0, self.x, self.y)
        self.send_finger(0, self.x + 100, self.y + 100)


    def send_finger(self, finger_number, x, y):
        report_type = 0x04 # REPORT_ID_MULTITOUCH

        misc = 0
        misc = misc | 0x02 # IN_RANGE
        misc = misc | 0x04 # DATA_VALID
        misc = misc | ((finger_number << 3) & 0xF8)

        self.send_raw_event(report_type, misc, x, y)


    def send_raw_event(self, report_type, misc, x, y):
        print("sending stuff")

        #Compose a SuperHID packet.
        #This emulates the "main.c" send_report() logic.
        data = bytes([ 
            report_type,
            misc,
            x & 0xFF,
            x >> 8,
            y & 0xFF,
            y >> 8
        ])

        self.endpoint.send(data)


class USBSuperHIDDevice(USBDevice):
    name = "SuperHID emulated model"

    def __init__(self, maxusb_app, verbose=0):
        config = USBConfiguration(
                1,                                        # index
                "SuperHID Super Device",                  # string desc
                [ USBSuperHIDInterface() ]                  # interfaces
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
                "SuperHID Touchscreen"       ,        # product string
                "S/N12345",                           # serial number string
                [ config ],
                verbose=verbose
        )

