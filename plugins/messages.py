from disco.bot import Plugin, Config
from types.giveaway import MessagesGiveaway
from types.participant import MessagesParticipant

class MessagesConfig(Config):

    master_guild_id = 360462032811851777
    staff_role_id = 360463652429496330

    blacklisted_channels = []

class MessagesPlugin(Plugin):

    def load(self, ctx):
        super(MessagesPlugin, self).load(ctx)
        self.handlers = []
        self.staff_handlers = []

        self.add_handler(self.giveaway_message_handler)

    @Plugin.listen("MessageCreate")
    def message_create_event(self, event):
        if event.message.guild is None:
            return
        
        if event.message.guild.id != self.config.master_guild_id:
            return
        
        if event.channel.message.id in self.config.blacklisted_channels:
            return
        
        for handler in self.handlers:
            handler(event.message)
        
        if self.config.staff_role_id in event.message.member.roles:
            for staff_handler in self.staff_handlers:
                staff_handler(event.message)
    
    def add_handler(self, handler):
        if not callable(handler):
            raise TypeError("handler must be of type function or callable but is type {typename}".format(
                typename=str(type(handler))
            ))
        self.handlers.append(handler)
    
    def add_staff_handler(self, staff_handler):
        if not callable(staff_handler):
            raise TypeError("staff_handler must be of type function or callable but is type {typename}".format(
                typename=str(type(staff_handler))
            ))
        self.staff_handlers.append(staff_handler)
    
    def giveaway_message_handler(self, message):
        base = self.bot.plugins["BasePlugin"]
        giveaways = base.get_giveaways(active=True, giveaway_type="message")
        for giveaway in giveaways:
            participant_id, participant = base.get_participant(giveaway.name, message.author.id, MessagesParticipant)
            if participant_id is None:
                base.create_participant(user_id = message.author.id, message_count=1, blacklisted=False)
                return
            participant.message_count += 1
            if giveaway.messages_required <= participant.message_count:
                participant.eligible = True
            base.update_participant(participant_id, participant.to_database_object())
    
    @Plugin.command("message", "<message_requirement:int> <name:str...>", group="new", level=100)
    def create_messages_giveaway(self, event, message_requirement, name):
        base = self.bot.plugins["BasePlugin"]
        base.create_giveaway(MessagesGiveaway, name=name, messages_required=message_requirement)
        event.msg.reply(":ok_hand: created giveaway `{giveaway_name}` with message goal of {message_goal}".format(
            giveaway_name=name,
            message_goal=str(message_requirement)
        ))
