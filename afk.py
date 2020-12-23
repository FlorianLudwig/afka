import click

import anre
import time

import logging
logging.basicConfig(level=logging.INFO)


class AFKArena:
    def __init__(self, ar: anre.Anre) -> None:
        self.ar = ar
        self.activity_name = "com.lilithgame.hgame.gp"
        self.current_screen = "campaign"
    
    def start_app(self):
        self.ar.start_app(self.activity_name)

    def close_app(self):
        self.ar.close_app(self.activity_name)

    def wait_until_loaded(self):
        while self.ar.get_pixel("50%", -1, update=True) != (242, 225, 145):
            time.sleep(0.1)
        
        print("done loading")

    def switch_tab(self, tab_name):
        if self.current_screen == tab_name:
            return

        x = {
            "ranhorn": "10%",
            "dark_forest": "30%",
            "campaign": "50%",
            "heros": "70%",
            "chat": "90%",
        }[tab_name]

        self.ar.tap(x, -10)

        # TODO verify we successfully reached desired screen

        self.current_screen = tab_name

    def loot_afk_chest(self):
        self.switch_tab("campaign")
        self.ar.tap("50%", -450)
        time.sleep(1)
        self.ar.tap("60%", "65%")

    def fight_campaign(self):
        self.switch_tab("campaign")
        self.ar.tap("50%", -280)

    def close(self):
        self.ar.close()


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

    # afk.switch_tab("campaign")
    # afk.switch_tab("ranhorn")
    # afk.switch_tab("dark_forest")
    afk.loot_afk_chest()

    afk.close()



if __name__ == "__main__":
    main()