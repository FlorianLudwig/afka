"""Interface to the game"""

import anre
import time

import pkg_resources
import logging


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

    def tap_image(self, image_name):
        collect = pkg_resources.resource_filename("afka", f"res/{image_name}.png")
        return self.ar.tap_image(collect)

    def find_image(self, image_name):
        collect = pkg_resources.resource_filename("afka", f"res/{image_name}.png")
        return self.ar.find_image(collect)

    def wait_for_image(self, image_name):
        collect = pkg_resources.resource_filename("afka", f"res/{image_name}.png")
        return self.ar.wait_for_image(collect)

    def loot_afk_chest(self):
        self.switch_tab("campaign")
        self.ar.tap("50%", -450)  # tap on pile of loot
        self.tap_image("collect_blue")  # tap collect button

    def loot_fast_rewards(self, spend_diamonds=False):
        self.switch_tab("campaign")
        self.tap_image("fast_rewards")
        self.wait_for_image("popup")

        conf, x, y = self.find_image("collect_for_50")
        if conf >= 0.8:
            if spend_diamonds:
                self.ar.tap(x, y)
                return
            else:
                print("fast rewards only available for diamonds and spend_diamonds=False")
                return

        self.tap_image("collect_yellow")

    def guild_hunt(self):
        self.switch_tab("ranhorn")
        self.ar.tap("30%", "15%")
        self.tap_image("guild_hunting")
        self.tap_image("guild_hunt_challenge") # start challenge
        time.sleep(0.1)
        self.tap_image("guild_hunt_challenge") # begin battle (confirms formation)
        time.sleep(60)
        self.tap_image("tap_to_close")

    def fight_campaign(self):
        self.switch_tab("campaign")
        self.ar.tap("50%", -280)

    def close(self):
        self.ar.close()