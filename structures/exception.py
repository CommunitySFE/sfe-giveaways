

class GiveawayResultFailure(Exception):

    def __init__(self, message):
        self.message = message

    def get_error_message(self):
        return ":no_entry_sign: {message}".format(message=self.message)