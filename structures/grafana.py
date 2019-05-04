import prometheus_client as prom


class MemberCountTracker:

    def __init__(self, registry):
        self.member_count_tracker = prom.Gauge("members", "member count (updated 30s)", registry=registry)

    def track_member_count(self, member_count):
        self.member_count_tracker.set(member_count)


class MessageCountTracker:

    def __init__(self, registry):
        self.message_count_tracker = prom.Gauge("message_count", "number of messages per 30s", registry=registry)

    def track_message_count(self, message_count):
        self.message_count_tracker.set(message_count)


class ChannelUsageTracker:

    def __init__(self, registry):
        self.channel_usage_tracker = prom.Gauge("channel_usage", "track how much a channel is used",
                                                ['channel_name'],
                                                registry=registry)

    def track_used_channel(self, channel_name):
        self.channel_usage_tracker.labels(channel_name=channel_name).inc()


class ActiveMemberTracker:
    """
    Tracks the amount of active members in a server.

    *Active members* are defined as people who have sent a message in the last hour.
    """

    def __init__(self, registry):
        self.active_member_tracker = prom.Gauge("active_members",
                                                "amount of active members (sent a message within 1 hour)",
                                                registry=registry)

    def track_active_members(self, active_member_count):
        self.active_member_tracker.set(active_member_count)

