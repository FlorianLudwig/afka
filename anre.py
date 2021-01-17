"""Android Remote"""

import time
from typing import Optional
import logging
import io
import os

import ppadb.client
import ppadb.device
import PIL.Image
import cv2 as cv
import numpy


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


def convert_to_bitmap(pixel):
    result = 1 if pixel > 200 else 0
    return result


class Anre:
    def __init__(self, ) -> None:
        self.client = ppadb.client.Client()
        self.device: Optional[ppadb.device.Device] = None
        self.screencap = None
        self._screencap_cv = None
        self.screencap_data = None
        self._image_cache = {}
        # ensure adb server is running
        os.system("adb start-server")

    @property
    def screencap_cv(self):
        if self._screencap_cv is None:
            open_cv_image = numpy.array(self.screencap.convert('RGB'))
            self._screencap_cv = open_cv_image[:, :, ::-1].copy()
        
        return self._screencap_cv
    
    def parse_coords(self, x, y):
        # ensure we know the screensize
        if not self.screencap:
            self.update_screencap()
        
        x = parse_coordinate(x, self.screencap.size[0])
        y = parse_coordinate(y, self.screencap.size[1])
        return x, y

    def select_device(self, preferred_devices: List[str]) -> None:
        devices = self.client.devices()
        
        if len(devices) == 0:
            raise IOError("no adb devices")

        # select preferred device
        for device_name in preferred_devices:
            for device in devices:
                if device.serial == device_name:
                    self.device = device
                    return
        
        # no devices matches any of the preferred device
        device_names = ", ".join(device.serial for device in devices)
        preferred_devices_names = ", ".join(preferred_devices)
        raise IOError(f"None of the available devices ({device_names}) matches any of the preferred devices ({preferred_devices_names})")

    def auto_select_device(self):
        devices = self.client.devices()
        if len(devices) == 0:
            raise IOError("no adb devices")
        
        if len(devices) == 1:
            self.device = devices[0]
            return
        
        device_names = ", ".join(device.serial for device in devices)
        raise IOError(f"Multiple adb devices found({device_names}), please specify desired device")
        
    def update_screencap(self) -> PIL.Image.Image:
        result = self.device.screencap()
        self.screencap = PIL.Image.open(io.BytesIO(result))
        self.screencap_data = self.screencap.load()
        self._screencap_cv = None
        return self.screencap
    
    def get_pixel(self, x, y, update=False):
        if update or not self.screencap:
            self.update_screencap()

        x, y = self.parse_coords(x, y)
        result = self.screencap_data[x, y]
        LOG.debug("pixel %i, %i color: %s", x, y, result)
        return result[:-1]  # remove alpha channel

    def tap(self, x, y) -> None:
        x, y = self.parse_coords(x, y)
        self.device.input_tap(x, y)

    def swipe(self, start_x, start_y, end_x, end_y) -> None:
        start_x, start_y = self.parse_coords(start_x, start_y)
        end_x, end_y = self.parse_coords(end_x, end_y)
        self.device.input_swipe(start_x, start_y, end_x, end_y)

    def start_app(self, activity) -> None:
        print(self.device.shell(f"monkey -p {activity} 1"))

    def close_app(self, activity) -> None:
        print(self.device.shell("am force-stop " + activity))
    
    def _load_image(self, image_path: str, scale: float=1.0) -> tuple:
        key = f'{image_path}.{scale}'
        if key not in self._image_cache:
            alpha = None
            src = PIL.Image.open(image_path)
            src = src.resize((int(src.size[0] * scale), int(src.size[1] * scale)))

            if src.mode not in ("RGB", "RGBA"):
                src = src.convert("RGBA")

            if src.mode == "RGBA":
                alpha_channel = src.getchannel("A")
                alpha_channel = alpha_channel.point(convert_to_bitmap)
                alpha = PIL.Image.merge("RGB", (alpha_channel, alpha_channel, alpha_channel))
                src = src.convert('RGB')
        
            open_cv_image = numpy.array(src)
            open_cv_image = open_cv_image[:, :, ::-1].copy()

            open_cv_mask = None
            if alpha:
                open_cv_mask = numpy.array(alpha)
                open_cv_mask = open_cv_mask[:, :, ::-1].copy()
            
            self._image_cache[key] = (open_cv_image, open_cv_mask)
        return self._image_cache[key]

    def find_image(self, image_path: str, scale: float=1.0) -> tuple:
        template, mask = self._load_image(image_path, scale)
        result = cv.matchTemplate(self.screencap_cv, template, cv.TM_CCOEFF_NORMED, None, mask)
        _, max_val, _, max_loc = cv.minMaxLoc(result)
        x = max_loc[0] + template.shape[1] / 2
        y = max_loc[1] + template.shape[0] / 2
        return max_val, x, y

    def wait_for_image(self, image_path: str, scale=1.0, timeout=60, threshold=0.9):
        start_time = time.time()

        if not self.screencap:
            self.update_screencap()
        
        while time.time() < start_time + timeout:
            max_val, x, y = self.find_image(image_path, scale=scale)
            if max_val >= threshold:
                return x, y
            self.update_screencap()
        
        raise ValueError(f"Image {image_path} not found on screen")

    def tap_image(self, image_path, scale=1.0, threshold=0.9, timeout=60):
        x, y = self.wait_for_image(image_path, scale=scale, timeout=timeout, threshold=threshold)
        self.tap(x, y)
        return x, y

    def close(self):
        pass