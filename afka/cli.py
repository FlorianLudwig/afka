import logging

import click
import anre

import afka.afk

LOG = logging.getLogger(__name__)


@click.command()
@click.option("--debug", is_flag=True, default=False)
def main(debug):
    if debug:
        LOG.info("starting in debug mode")
        import anre_debug
        ar = anre_debug.AnreDebug()
    else:
        ar = anre.Anre()
    ar.auto_select_device()

    LOG.info("device selected: " + ar.device.serial)

    afk = afka.afk.AFKArena(ar)

    afk.close_app()
    afk.start_app()
    afk.wait_until_loaded()

    afk.fight_campaign()
    afk.loot_afk_chest()
    afk.loot_fast_rewards()
    afk.guild_hunt()
    afk.friends_send_and_receive()
    afk.collect_mail()
    afk.collect_quest_rewards()
    
    afk.ar.update_screencap()
    afk.ar.tap(10, 10)

    afk.close()


if __name__ == "__main__":
    main()