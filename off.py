#! /usr/bin/env python

import sys
import time
import os
from socket import error as socket_error
import subprocess

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from mpd import MPDClient

serial = i2c(port=0, address=0x3C)
device = sh1106(serial, rotate=2)

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

device.hide()
