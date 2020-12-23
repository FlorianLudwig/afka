import click
import anre

import afka.afk


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

    afk = afka.afk.AFKArena(ar)

    # afk.close_app()
    # afk.start_app()
    # afk.wait_until_loaded()

    # afk.switch_tab("campaign")
    # afk.switch_tab("ranhorn")
    # afk.switch_tab("dark_forest")
    # afk.loot_afk_chest()
    afk.loot_fast_rewards()

    afk.ar.update_screencap()
    afk.ar.tap(10, 10)

    afk.close()



if __name__ == "__main__":
    main()