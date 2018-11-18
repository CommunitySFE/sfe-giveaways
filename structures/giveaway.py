from structures.database import DatabaseObject


class Giveaway(DatabaseObject):
    """
    Base class for giveaways
    """

    def __init__(self):
        super().__init__()
        self.active = False
        self.name = "unnamed giveaway"
        self.autopick = False
        self.autopick_time = None
        self.pick_random = False
        self.giveaway_type = "base"


class MessagesGiveaway(Giveaway):

    def __init__(self):
        super().__init__()
        self.messages_required = 100
        self.giveaway_type = "message"
