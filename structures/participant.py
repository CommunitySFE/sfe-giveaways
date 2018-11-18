from structures.database import DatabaseObject


class Participant(DatabaseObject):

    def __init__(self):
        super().__init__()
        self.user_id = 0
        self.eligible = False
        self.blacklisted = False
        self.giveaway = None


class MessagesParticipant(Participant):

    def __init__(self):
        super().__init__()
        self.message_count = 0
