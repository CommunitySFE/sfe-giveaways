from prometheus_client import start_http_server, CollectorRegistry
from disco.bot import Plugin, Config
import structures.grafana as grafana_structs
import disco.types.base


class GrafanaPluginConfig(Config):

    prometheus_server_port = 9091
    master_guild_id = 0


@Plugin.with_config(GrafanaPluginConfig)
class GrafanaPlugin(Plugin):

    def load(self, ctx):
        super().load(ctx)
        self.registry = CollectorRegistry()
        self.member_count_tracker = grafana_structs.MemberCountTracker(self.registry)
        self.message_count_tracker = grafana_structs.MessageCountTracker(self.registry)
        self.temporary_message_count = 0
        start_http_server(self.config.prometheus_server_port, registry=self.registry)

    @Plugin.schedule(30, True, True)
    def log_message_count(self):
        self.message_count_tracker.track_message_count(self.temporary_message_count)
        self.temporary_message_count = 0

    @Plugin.listen("MessageCreate")
    def on_message(self, msg):
        if msg.guild is None:
            return
        if msg.guild.id != self.config.master_guild_id:
            return
        self.temporary_message_count += 1

    @Plugin.schedule(30, True, True)
    def log_member_count(self):
        if self.config.master_guild_id not in self.client.state.guilds:
            return
        member_count = self.client.state.guilds[self.config.master_guild_id].member_count
        if member_count == 0:
            print("skipping logging member count - guild has no members")
            return
        self.member_count_tracker.track_member_count(member_count)

