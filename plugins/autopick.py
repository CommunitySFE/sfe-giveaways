from disco.bot import Plugin, Config
from structures.exception import GiveawayResultFailure
from structures.giveaway import Giveaway
import sched
import time


class AutopickConfig(Config):

    log_channel_id = 0


@Plugin.with_config(AutopickConfig)
class AutopickPlugin(Plugin):

    def load(self, ctx):
        super(AutopickPlugin, self).load(ctx)
        self.scheduler = sched.scheduler(time.time, time.sleep)

    @Plugin.schedule(3600, True, True)
    def automatic_pick(self):
        base_plugin = self.bot.plugins["BasePlugin"]
        active_giveaways = base_plugin.get_giveaways(Giveaway, active=True, autopick=True, pick_random=True)
        for active_giveaway in active_giveaways:
            if active_giveaway.autopick_time is None:
                continue
            if active_giveaway.autopick_time >= time.time() + (3600*1000):
                continue
            run_time = active_giveaway.autopick_time - time.time()
            if run_time <= 0:
                run_time = 2
            self.scheduler.enter(
                run_time,
                0,
                self.pick_giveaway,
                argument=(active_giveaway,)
            )
            self.scheduler.run()

    def pick_giveaway(self, *args):
        giveaway = args[0]
        base = self.bot.plugins["BasePlugin"]
        log_channel = self.client.api.channels_get(self.config.log_channel_id)

        try:
            result = base.pick_giveaway(giveaway)
        except GiveawayResultFailure as failure:
            log_channel.send_message(":x: Failed to pick user in giveaway {name} (`{reason}`)".format(
                name=giveaway.name,
                reason=failure.message
            ))
            return

        log_channel.send_message(":tada: <@{id}> won the giveaway **{giveaway_name}**".format(
            id=result,
            giveaway_name=giveaway.name
        ))

        base.update_giveaway(giveaway.mongodb_id, active=False)
