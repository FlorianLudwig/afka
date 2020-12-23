"""Android Remote"""

from typing import Optional
import logging

import io
import ppadb.client
import ppadb.device
import PIL.Image


LOG = logging.getLogger(__name__)


def parse_coordinate(value, v100):
    if isinstance(value, float):
        value = int(value)
    
    if isinstance(value, str):
        if not value.endswith("%"):
            raise ValueError("cooridantes must be int, float or in %")
        
        value = value.strip("% ")
        value = float(value)
        value = int(float(value) / 100 * v100)
    
    if isinstance(value, int):
        return value if value >= 0 else v100 + value
    
    raise ValueError("Unknown cooridate " + repr(value))


class Anre:
    def __init__(self, ) -> None:
        self.client = ppadb.client.Client()
        self.device: Optional[ppadb.device.Device] = None
        self.screencap = None
        self.screencap_data = None
    
    def parse_coords(self, x, y):
        # ensure we know the screensize
        if not self.screencap:
            self.update_screencap()
        
        x = parse_coordinate(x, self.screencap.size[0])
        y = parse_coordinate(y, self.screencap.size[1])
        return x, y

    def select_device(self, serial):
        self.device = self.client.device(serial)

    def auto_select_device(self, preferred_devices=None):
        devices = self.client.devices()
        if len(devices) == 0:
            raise IOError("no devices")
        elif len(devices) == 1:
            self.device = devices[0]
        else:
            # TODO
            raise IOError("multiple devices")
        
    def update_screencap(self) -> PIL.Image.Image:
        result = self.device.screencap()
        self.screencap = PIL.Image.open(io.BytesIO(result))
        self.screencap_data = self.screencap.load()
        return self.screencap
    
    def get_pixel(self, x, y, update=False):
        if update or not self.screencap:
            self.update_screencap()

        x, y = self.parse_coords(x, y)
        result = self.screencap_data[x, y]
        LOG.debug("pixel %i, %i color: %s", x, y, result)
        return result[:-1]  # remove alpha channel

    def tap(self, x, y):
        x, y = self.parse_coords(x, y)
        self.device.input_tap(x, y)

    def swipe(self, start_x, start_y, end_x, end_y):
        start_x, start_y = self.parse_coords(start_x, start_y)
        end_x, end_y = self.parse_coords(end_x, end_y)
        self.device.input_swipe(start_x, start_y, end_x, end_y)

    def start_app(self, activity):
        print(self.device.shell(f"monkey -p {activity} 1"))

    def close_app(self, activity):
        print(self.device.shell("am force-stop " + activity))
    
    def close(self):
        pass