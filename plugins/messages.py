from disco.bot import Plugin, Config

class MessagesConfig(Config):

    master_guild_id = 360462032811851777
    staff_role_id = 360463652429496330

    blacklisted_channels = []

class MessagesPlugin(Plugin):

    def load(self, ctx):
        super(MessagesPlugin, self).load(ctx)
        self.handlers = []
        self.staff_handlers = []

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
            raise TypeError("handler must be of type function or callable")
        self.handlers.append(handler)
    
    def add_staff_handler(self, staff_handler):
        if not callable(staff_handler):
            raise TypeError("staff_handler must be of type function or callable")
        self.staff_handlers.append(staff_handler)
    
    def giveaway_message_handler(self, message):
        base = self.bot.plugins["BasePlugin"]
        giveaways = base.get_giveaways(active=True, giveaway_type="message")
        for giveaway in giveaways:
            # TODO finish giveaway message handler
            participant_id, participant = base.get_participants_in_giveaway(giveaway.name)


    

