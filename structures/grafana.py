import prometheus_client as prom


class MemberCountTracker:

    def __init__(self, registry):
        self.member_count_tracker = prom.Gauge("members", "member count", registry=registry)

    def track_member_count(self, member_count):
        self.member_count_tracker.set(member_count)


class MessageCountTracker:

    def __init__(self, registry):
        self.message_count_tracker = prom.Gauge("message_count", "number of messages per minute", registry=registry)

    def track_message_count(self, message_count):
        self.message_count_tracker.set(message_count)