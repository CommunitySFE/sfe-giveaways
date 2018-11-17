from types.database import DatabaseObject
import time

class Giveaway(DatabaseObject):
    """
    Base class for giveaways
    """

    active = False
    name = "unnamed giveaway"
    ends = time.ctime()
    pick_random = False
    giveaway_type = "base"


class MessagesGiveaway(Giveaway):

    messages_required = 100
    giveaway_type = "message"

    
