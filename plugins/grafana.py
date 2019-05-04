from prometheus_client import start_http_server, CollectorRegistry
from disco.bot import Plugin, Config
import structures.grafana as grafana_structs


class GrafanaPluginConfig(Config):

    prometheus_server_port = 9091
    master_guild_id = 0
    channel_blacklist = []


@Plugin.with_config(GrafanaPluginConfig)
class GrafanaPlugin(Plugin):

    def load(self, ctx):
        super().load(ctx)
        self.registry = CollectorRegistry()
        self.member_count_tracker = grafana_structs.MemberCountTracker(self.registry)
        self.message_count_tracker = grafana_structs.MessageCountTracker(self.registry)
        self.active_member_tracker = grafana_structs.ActiveMemberTracker(self.registry)
        self.channel_usage_tracker = grafana_structs.ChannelUsageTracker(self.registry)
        self.temporary_message_count = 0
        self.active_members = []
        self.cached_member_count = 0
        start_http_server(self.config.prometheus_server_port, registry=self.registry)

    @Plugin.schedule(30, True, True)
    def log_message_count(self):
        self.message_count_tracker.track_message_count(self.temporary_message_count)
        self.temporary_message_count = 0

    @Plugin.listen("MessageCreate")
    def on_message(self, message):
        if message.guild is None:
            return
        if int(message.guild.id) != int(self.config.master_guild_id):
            return
        if int(message.channel.id) in self.config.channel_blacklist:
            return
        if int(message.author.id) not in self.active_members:
            self.active_members.append(message.author.id)
        self.temporary_message_count += 1
        self.channel_usage_tracker.track_used_channel(message.channel.name)

    @Plugin.schedule(30, True, True)
    def log_member_count(self):
        if self.config.master_guild_id not in self.client.state.guilds:
            return
        if self.client.state.guilds[self.config.master_guild_id].member_count == 0:
            return
        member_count = len(self.client.state.guilds[self.config.master_guild_id].members)
        self.member_count_tracker.track_member_count(member_count)

    @Plugin.schedule(3600, True, True)
    def track_active_members(self):
        active_members = len(self.active_members)
        self.active_member_tracker.track_active_members(active_members)
        self.active_members.clear()

