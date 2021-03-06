"""Interface to the game"""

import anre
import time
import enum
import logging

import pkg_resources


class MainScreen(enum.Enum):
    RANHORN = "ranhorn"
    DARK_FOREST = "dark_forest"
    CAMPAIGN = "campaign"
    HEROS = "heros"
    CHAT = "chat"


class Screen(enum.Enum):
    MAIL = "mail"
    BAG = "bag"
    FRIENDS = "friends"
    QUESTS_DAILIES = "quests_dailies"
    QUESTS_WEEKLY = "quests_weekly"
    QUESTS_CAMPAIGN = "quests_campaign"
    BOUNTY_QUESTS = "bounty_quests"
    BOUNTY_TEAM = "bounty_team"


logging.basicConfig(level=logging.INFO)

LOG = logging.getLogger(__name__)
AVOID_DOUBLE_TAB_DELAY = 0.1


class AFKArena:
    def __init__(self, ar: anre.Anre) -> None:
        self.ar = ar
        self.activity_name = "com.lilithgame.hgame.gp"
        self.current_screen = MainScreen.CAMPAIGN
    
    def start_app(self):
        self.ar.start_app(self.activity_name)

    def close_app(self):
        self.ar.close_app(self.activity_name)

    def wait_until_loaded(self):
        LOG.info("waiting till app is loaded")
        while self.ar.get_pixel("50%", -1, update=True) != (242, 225, 145):
            time.sleep(0.1)
        
        LOG.info("afk arena done loading")

    def switch_to(self, target):
        LOG.debug("switch from %s to %s", self.current_screen, target)
        if self.current_screen == target:
            return

        main_screens = {
            MainScreen.RANHORN: "10%",
            MainScreen.DARK_FOREST: "30%",
            MainScreen.CAMPAIGN: "50%",
            MainScreen.HEROS: "70%",
            MainScreen.CHAT: "90%",
        }

        if target == Screen.FRIENDS:
            self.switch_to(MainScreen.CAMPAIGN)
            self.click_all_image("menu_arrow")
            self.tap_image("friends")
        
        elif target == Screen.MAIL:
            self.switch_to(MainScreen.CAMPAIGN)
            self.click_all_image("menu_arrow", timeout=3)
            self.tap_image("mail")
        
        elif target == "guild":
            self.switch_to(MainScreen.RANHORN)
            self.ar.tap("30%", "15%")
            time.sleep(AVOID_DOUBLE_TAB_DELAY)
        
        elif target == Screen.QUESTS_DAILIES:
            self.switch_to(MainScreen.CAMPAIGN)
            self.tap_image("quests")
            time.sleep(AVOID_DOUBLE_TAB_DELAY)

        elif target == Screen.BOUNTY_QUESTS:
            self.switch_to(MainScreen.DARK_FOREST)
            self.tap_image("bounty_board")
            time.sleep(AVOID_DOUBLE_TAB_DELAY)
        elif target == "guild_hunting":
            self.switch_to("guild")
            self.tap_image("guild_hunting")

        elif target in main_screens:
            # we want to go to one of the main screens, ensure there
            # is no back button visible (meaning we are in one of the)
            # subscreens
            self.click_all_image("back", timeout=5)
            x = main_screens[target]
            self.ar.tap(x, -10)
        else:
            raise AttributeError(f"Unkown screen '{target}'")

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
        LOG.info("starting loot_afk_chest")
        self.switch_to(MainScreen.CAMPAIGN)
        self.ar.tap("50%", -450)  # tap on pile of loot
        self.tap_image("blue_button")  # tap collect button
        time.sleep(AVOID_DOUBLE_TAB_DELAY)
        LOG.info("done loot_afk_chest")

    def loot_fast_rewards(self, spend_diamonds=False):
        LOG.info("starting loot_fast_rewards")
        self.switch_to(MainScreen.CAMPAIGN)
        self.tap_image("fast_rewards")
        self.wait_for_image("popup")

        conf, x, y = self.find_image("collect_for_50")
        if conf >= 0.8:
            if spend_diamonds:
                self.ar.tap(x, y)
            else:
                LOG.info("fast rewards only available for diamonds and spend_diamonds=False")
                self.ar.tap(10, 10)
                time.sleep(AVOID_DOUBLE_TAB_DELAY)
                LOG.info("done loot_fast_rewards")
                return

        else:
            self.tap_image("collect_yellow")
        time.sleep(AVOID_DOUBLE_TAB_DELAY)
        self.ar.tap(10, 10)
        time.sleep(AVOID_DOUBLE_TAB_DELAY)
        self.ar.tap(10, 10)
        time.sleep(AVOID_DOUBLE_TAB_DELAY)
        LOG.info("done loot_fast_rewards")

    def friends_send_and_receive(self):
        LOG.info("starting friends_send_and_receive")
        self.switch_to(Screen.FRIENDS)
        # tap Send & Receive button
        self.tap_image("and")
        LOG.info("done friends_send_and_receive")
    
    def collect_mail(self):
        LOG.info("starting collect_mail")
        self.switch_to(Screen.MAIL)
        self.tap_image("blue_button")
        LOG.info("done collect_mail")

    def guild_hunt(self):
        LOG.info("starting guild_hunt")
        self.switch_to("guild_hunting")
        for _ in range(2):
            try:
                self.tap_image("guild_hunt_challenge", timeout=10) # start challenge
            except ValueError:
                print("Looks like guild hunting already done")
                break
            time.sleep(0.1)
            self.tap_image("guild_hunt_challenge") # begin battle (confirms formation)
            time.sleep(60)
            self.tap_image("tap_to_close")
            self.tap_image("tap_to_close")
        LOG.info("done guild_hunt")

    def click_all_image(self, image_name, scale=1.0, threshold=0.9, timeout=5):
        LOG.debug("Click all %s images", image_name)
        while True:
            self.ar.update_screencap()
            try:
                self.tap_image(image_name, scale=scale, threshold=threshold, timeout=timeout)
            except ValueError:
                return

    def collect_quest_rewards(self):
        LOG.info("starting collect_quest_rewards")
        self.switch_to(Screen.QUESTS_DAILIES)
        self.click_all_image("blue_button", threshold=0.7, scale=0.85)
        self.click_all_image("quest_reward", threshold=0.7, scale=0.85)

        # self.switch_to(Screen.QUESTS_DAILIES)

        # self.switch_to("quests_campaign")
        LOG.info("done collect_quest_rewards")

    def fight_campaign(self):
        LOG.info("starting fight_campaign")
        self.switch_to(MainScreen.CAMPAIGN)
        self.tap_image("guild_hunt_challenge") # begin battle
        time.sleep(1)
        self.ar.update_screencap()
        self.tap_image("guild_hunt_challenge") # begin battle (confirms formation)
        self.tap_image("touch_screen_to_continue", timeout=160)
        self.tap_image("touch_screen_to_continue", timeout=10)
        LOG.info("done collect_quest_rewards")
        

    def close(self):
        self.ar.close()