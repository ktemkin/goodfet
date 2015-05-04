#!/usr/bin/env python3
#
# facedancer-keyboard.py

from Facedancer import *
from MAXUSBApp import *
from USBTouchscreen import *

sp = GoodFETSerialPort()
fd = Facedancer(sp, verbose=1)
u  = MAXUSBApp(fd, verbose=2)

data = open("replay_data.txt")
#data = open("/tmp/small_screen_replay.txt")

d = USBReplayTouchscreen(u, data, verbose=4)

d.connect()

try:
    d.run()
# SIGINT raises KeyboardInterrupt
except KeyboardInterrupt:
    d.disconnect()
