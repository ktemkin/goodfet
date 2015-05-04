# USBTouchscreen.py
#
# Contains class definitions to implement a USB touchscreen, to test
# the use of uncertified touchscreens on Windows 8 installations.

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBEndpoint import *

REPORT_ID_MOUSE        = 0x02
REPORT_ID_MULTITOUCH   = 0x04
REPORT_ID_MT_MAX_COUNT = 0x10

class USBTouchscreenInterface(USBInterface):
    name = "USB Touchscreen interface"



    def __init__(self, replay_file_data, verbose=0):
        """ Define the behavior of the USB interface that will drive our HID touchscreen. """

        #TODO: Generalize!
        self.replay_file = replay_file_data

        #The first entry in the replay file should be the 
        report_descriptor = self.get_next_replay_packet()

        report_descriptor_length_lsb =     len(report_descriptor) % 256
        report_descriptor_length_msb = int(len(report_descriptor) / 256)

        #TODO: Replace me with a python struct.
        hid_descriptor = [0x09, 0x21, 0x10, 0x01, 0x00, 0x01, 0x22, report_descriptor_length_lsb, report_descriptor_length_msb]


        #Provide each of the descriptors that will be used to identify the target USB device.
        descriptors = { 
                USB.desc_type_hid    : bytes(hid_descriptor),
                USB.desc_type_report : bytes(report_descriptor)
        }

        self.endpoint = USBEndpoint(
                3,          # endpoint number
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                4,         # polling interval, see USB 2.0 spec Table 9-13
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
            
        self.queue = []

        while True:
            packet = self.get_next_replay_packet()
            
            if packet:
                self.queue.append(packet)
            else:
                break


    def get_next_replay_packet(self):
        """ Quick, completely non-general method for reading usbhid-dump data. """

        packet = []

        #Read lines until we read an empty line.
        while True:

            #Read a single line.
            line = self.replay_file.readline()

            #... and trim any leading/trailing whilespice.
            line = line.strip()

            #If it contains the word STREAM, it's a header line, and we'll 
            #skip it.
            if "STREAM" in line:
                continue

            if "DESCRIPTOR" in line:
                continue

            #If the line is empty, stop parsing.
            if not line:
                break

            #Otherwise, split it into bytes...
            octets = [int(byte, 16) for byte in line.split()]

            #... and add the octets to the packet.
            packet.extend(octets)


        #Return a binary packet.
        return bytes(packet)


    def handle_get_report(self, device):

        #Read the next HID packet to be sent from the replay file...
        if self.queue:
            packet_one = self.queue.pop(0)

        else:
            return

        device.send_control_message(packet_one)




    def handle_buffer_available(self):
        """ Handle HID data updates (interrupts). """

        #Read the next HID packet to be sent from the replay file...
        if self.queue:
            packet = self.queue.pop(0)
        else:
            return

        #... otherwise, send it to the device directly.
        self.endpoint.send(packet)



class USBReplayTouchscreen(USBDevice):
    name = "USB touchscreen device"

    def __init__(self, maxusb_app, replay_file_data, verbose=0):

        interface = USBTouchscreenInterface(replay_file_data, verbose=verbose)

        config = USBConfiguration(
                1,                              # index
                "Emulated multitouch screen",   # string desc
                [ interface ]   # interfaces
        )

        USBDevice.__init__(
                self,
                maxusb_app,
                0,                      # device class
                0,                      # device subclass
                0,                      # protocol release number
                64,                     # max packet size for endpoint 0
                0x2808,                 # vendor id
                0x81C9,                 # product id
                0x0,                 # device revision
                "AIS",                  # manufacturer string
                "Emulated touchscreen", # product string
                "0",             # serial number string
                [ config ],
                verbose=verbose
        )

