from disco.bot import Plugin, Config


class AutopickConfig(Config):

    enabled = False


@Plugin.with_config(AutopickConfig)
class AutopickPlugin(Plugin):


    @Plugin.schedule(3600, True, True)
    def automatic_pick(self):
        base_plugin = self.bot.plugins["BasePlugin"]
        active_giveaways = base_plugin.get_giveaways(active=True, autopick=True)
        for active_giveaway in active_giveaways:
            if active_giveaway.autopick_time is None:
                continue
            if active_giveaway.autopick_time >= 3600:
                continue
            # TODO schedule ending the giveaway.
