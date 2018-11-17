from types.database import DatabaseObject


class Participant(DatabaseObject):

    user_id = 0
    eligible = False
    blacklisted = False
    giveaway = "unknown_giveaway"


class MessagesParticipant(Participant):

    message_count = 0