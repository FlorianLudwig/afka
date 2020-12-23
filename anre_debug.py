from typing import Optional

import collections
import logging
import threading
from click.globals import resolve_color_default

import PIL.Image
import pygame

import anre


LOG = logging.getLogger(__name__)
FONT = None
RED = (255, 0, 0)

def calc_scale(src_width, src_height, dst_width, dst_height):
    """scale into max size but do not upscale"""
    scale = min(dst_width / src_width, dst_height / src_height)
    return min(scale, 1)


class DbgLog:
    def __init__(self) -> None:
        pass

    def draw_on_screenshot(self, target, scale=1):
        pass

    def draw_log(self, target, start_x, start_y) -> int:
        pass


class GetPixel(DbgLog):
    def __init__(self, x, y, result, target_area) -> None:
        self.x = x
        self.y = y
        self.result = result
        self.target_area = target_area
        self.textsurface = FONT.render(f'get_pixel {x} {y} = {result}', True, (255, 255, 255), (0, 0, 0))
    
    def draw_on_screenshot(self, target, scale=1):
        pygame.draw.line(target, RED, (self.x*scale-10, self.y*scale), (self.x*scale-1, self.y*scale), 5)
        pygame.draw.line(target, RED, (self.x*scale+1, self.y*scale), (self.x*scale+10, self.y*scale), 5)

        pygame.draw.line(target, RED, (self.x*scale, self.y*scale-10), (self.x*scale, self.y*scale-1), 5)
        pygame.draw.line(target, RED, (self.x*scale, self.y*scale+1), (self.x*scale, self.y*scale+10), 5)

    def draw_log(self, target, start_x, start_y) -> int:
        target.blit(self.target_area, (start_x, start_y))
        target.blit(self.textsurface, (start_x + 60, start_y))

        # pygame.draw.line(target, RED, (start_x, start_x), (start_x, start_x), 5)


class AnreDebug(anre.Anre):
    def __init__(self) -> None:
        global FONT
        super().__init__()

        self.dbg_latest_screenshot = None

        pygame.init()
        FONT = pygame.font.SysFont('Cantarel', 12)
        self.dbg_screen = pygame.display.set_mode((1000, 1000))
        self.dbg_thread = threading.Thread(target=self.dbg_draw_loop)
        self.dbg_thread.start()
        self.dbg_scale = 1
        self.dbg_log = collections.deque(maxlen=50)

    def update_screencap(self) -> PIL.Image.Image:
        result = super().update_screencap()
        self.dbg_scale = calc_scale(*result.size, 500, 1000)
        
        target_size = [int(i * self.dbg_scale) for i in result.size]
        print(self.dbg_scale, target_size)
        scaled = result.resize(target_size)
        raw = scaled.tobytes("raw", 'RGBA')
        surface = pygame.image.fromstring(raw, scaled.size, 'RGBA')

        self.dbg_latest_screenshot = surface
        return result

    def get_pixel(self, x, y, update):
        result = super().get_pixel(x, y, update=update)
        target_area = self.screencap.crop((x - 5, y - 5, x+6, y+6))
        target_area = target_area.resize((55, 55), PIL.Image.NEAREST)
        raw = target_area.tobytes("raw", 'RGBA')
        surface = pygame.image.fromstring(raw, target_area.size, 'RGBA')
        self.dbg_log.append(GetPixel(x, y, result, surface))
        return result

    def dbg_draw_loop(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if self.dbg_latest_screenshot:
                self.dbg_screen.blit(self.dbg_latest_screenshot, (0, 0))
            

            # create copy of log as it might mutate through the other thread
            log = list(self.dbg_log)
            if log:
                log[-1].draw_on_screenshot(self.dbg_screen, self.dbg_scale)

                y = 5
                for entry in log:
                    entry.draw_log(self.dbg_screen, 510, y)
                    y += 60

            pygame.display.flip()
            clock.tick(30)
        
        pygame.quit()
        # also stop rest of the program?