import click

import anre
import time

import logging
logging.basicConfig(level=logging.DEBUG)


class AFKArena:
    def __init__(self, ar: anre.Anre) -> None:
        self.ar = ar
    
    def close_app(self):
        pass

    def start_app(self):
        pass
        
    def wait_until_loaded(self):
        while self.ar.get_pixel(450, 1775, update=True) != (0xcc, 0x92, 0x61):
            time.sleep(1)
        

    # t = time.time()
    # img = ar.screencap_pillow()
    # print(time.time() - t)
    # pixel_data = img.load()
    
    # print(pixel_data)

@click.command()
@click.option("--debug", is_flag=True, default=False)
def main(debug):
    if debug:
        print("starting in debug mode")
        import anre_debug
        ar = anre_debug.AnreDebug()
    else:
        ar = anre.Anre()
    ar.auto_select_device()

    print("device selected:", ar.device.serial)

    afk = AFKArena(ar)

    afk.close_app()
    afk.start_app()
    afk.wait_until_loaded()

    time.sleep(160)



if __name__ == "__main__":
    main()