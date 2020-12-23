"""Interface to the game"""

from PIL.ImageOps import scale
import anre
import time
import enum

import pkg_resources
import logging


class Screen(enum.Enum):
    pass


AVOID_DOUBLE_TAB_DELAY = 0.1


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

    def switch_to(self, target):
        if self.current_screen == target:
            return

        main_screens = {
            "ranhorn": "10%",
            "dark_forest": "30%",
            "campaign": "50%",
            "heros": "70%",
            "chat": "90%",
        }

        if target in main_screens:
            # TODO check if tabs are visible
            x = main_screens[target]
            self.ar.tap(x, -10)

        if target == "guild":
            self.switch_to("ranhorn")
            self.ar.tap("30%", "15%")
            time.sleep(AVOID_DOUBLE_TAB_DELAY)
        
        if target == "quests_dailies":
            self.tap_image("quests")
            time.sleep(AVOID_DOUBLE_TAB_DELAY)

        # TODO verify we successfully reached desired screen
        self.current_screen = target

    def tap_image(self, image_name, scale=1.0, threshold=0.9, timeout=60):
        collect = pkg_resources.resource_filename("afka", f"res/{image_name}.png")
        return self.ar.tap_image(collect, scale=scale, threshold=threshold, timeout=timeout)

    def find_image(self, image_name, scale=1.0):
        collect = pkg_resources.resource_filename("afka", f"res/{image_name}.png")
        return self.ar.find_image(collect, scale=scale)

    def wait_for_image(self, image_name, scale=1.0, timeout=60, threshold=0.9):
        collect = pkg_resources.resource_filename("afka", f"res/{image_name}.png")
        return self.ar.wait_for_image(collect, timeout=timeout, threshold=threshold, scale=scale)

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
        self.switch_to("guild")
        self.tap_image("guild_hunting")
        self.tap_image("guild_hunt_challenge") # start challenge
        time.sleep(0.1)
        self.tap_image("guild_hunt_challenge") # begin battle (confirms formation)
        time.sleep(60)
        self.tap_image("tap_to_close")

    def click_all_image(self, image_name, scale=1.0, threshold=0.9):
        while True:
            self.ar.update_screencap()
            try:
                self.tap_image(image_name, scale=scale, threshold=threshold, timeout=10)
            except ValueError:
                return

    def collect_quest_rewards(self):
        self.switch_to("quests_dailies")
        self.click_all_image("collect_blue", threshold=0.7, scale=0.85)

        # self.switch_to("quests_weeklies")

        # self.switch_to("quests_campaign")

    def fight_campaign(self):
        self.switch_tab("campaign")
        self.ar.tap("50%", -280)

    def close(self):
        self.ar.close()