from disco.bot import Plugin, Config
from disco.types.guild import GuildMember
from disco.types.message import MessageEmbed
from disco.api.http import APIException
from structures.giveaway import MessagesGiveaway, StaffQuota
from structures.participant import MessagesParticipant
import datetime


class MessagesConfig(Config):

    master_guild_id = 360462032811851777
    staff_role_id = 360463652429496330

    blacklisted_channels = [381913081069961217]

    green_tick_emote = "<:GreenTick:0>"
    red_tick_emote = "<:RedTick:0>"


@Plugin.with_config(MessagesConfig)
class MessagesPlugin(Plugin):

    def load(self, ctx):
        super(MessagesPlugin, self).load(ctx)
        self.handlers = []
        self.staff_handlers = []

        self.add_handler(self.giveaway_message_handler)
        self.add_staff_handler(self.staff_quota_handler)

    @Plugin.listen("MessageCreate")
    def message_create_event(self, event):
        if event.message.guild is None:
            return
        
        if event.message.guild.id != self.config.master_guild_id:
            return
        
        if event.message.channel.id in self.config.blacklisted_channels:
            return

        if event.message.author.bot:
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
        giveaways = base.get_giveaways(MessagesGiveaway, active=True, giveaway_type="message")
        for giveaway in giveaways:
            participant_id, participant = base.get_participant(
                giveaway.mongodb_id, message.author.id, MessagesParticipant
            )
            if participant_id is None:
                base.create_participant(
                    MessagesParticipant,
                    user_id=message.author.id,
                    message_count=1,
                    blacklisted=False,
                    giveaway=giveaway.mongodb_id
                )
                return
            participant.message_count += 1
            if giveaway.messages_required <= participant.message_count:
                participant.eligible = True
            base.update_participant(participant_id, **participant.to_database_object())

    def staff_quota_handler(self, message):
        # I know it's copy and paste, but it works.
        base = self.bot.plugins["BasePlugin"]
        quotas = base.get_giveaways(StaffQuota, active=True, giveaway_type="staff quota")
        for quota in quotas:
            participant_id, participant = base.get_participant(
                quota.mongodb_id, message.author.id, MessagesParticipant
            )
            if participant_id is None:
                base.create_participant(
                    MessagesParticipant,
                    user_id=message.author.id,
                    message_count=1,
                    blacklisted=False,
                    giveaway=quota.mongodb_id
                )
                return
            participant.message_count += 1
            if quota.messages_required <= participant.message_count:
                participant.eligible = True
            base.update_participant(participant_id, **participant.to_database_object())
    
    @Plugin.command("message", "<message_requirement:int> <name:str...>", group="giveaway new", level=100)
    def create_messages_giveaway(self, event, message_requirement, name):
        base = self.bot.plugins["BasePlugin"]
        base.create_giveaway(MessagesGiveaway, name=name, messages_required=message_requirement, active=True)
        event.msg.reply(":ok_hand: created giveaway `{giveaway_name}` with message goal of {message_goal}".format(
            giveaway_name=name,
            message_goal=str(message_requirement)
        ))

    @Plugin.command("new", "<message_requirement:int>", group="quota", level=100)
    def create_new_quota(self, event, message_requirement):
        if event.msg.guild == self.config.master_guild_id:
            event.msg.reply(":no_entry_sign: this command must be done on the staff server.")
            return
        base = self.bot.plugins["BasePlugin"]
        year = datetime.datetime.now().date().isocalendar()[0]
        week = datetime.datetime.now().date().isocalendar()[1]
        is_sunday = (datetime.datetime.now().weekday() + 1) % 7
        if is_sunday == 0:
            week += 1
        quota_name = "{year}-{week}_staff-quota".format(
            year=year,
            week=week
        )
        if base.get_giveaway(quota_name) is not None:
            event.msg.reply(":no_entry_sign: a quota was already made this week")
            return
        base.create_giveaway(StaffQuota, name=quota_name, messages_required=message_requirement, active=True)
        event.msg.reply(":ok_hand: created quota named `{quota_name}` with message requirement {msg_req}".format(
            quota_name=quota_name,
            msg_req=message_requirement
        ))

    @Plugin.command("check", "<quota_name:str>", group="quota", level=100)
    def check_quota(self, event, quota_name):
        base = self.bot.plugins["BasePlugin"]
        moderators = base.get_staff_in_quota(quota_name, MessagesParticipant)
        if moderators is None:
            event.msg.reply(":no_entry_sign: unknown quota.")
            return
        quota_fail_embed = MessageEmbed()
        for moderator in moderators:
            if not moderator.eligible:
                quota_fail_embed.add_field(
                    value="<@{id}>".format(id=moderator.user_id),
                    name="Message count: {count}".format(count=moderator.message_count)
                )
        if len(quota_fail_embed.fields) == 0:
            quota_fail_embed.title = "{green_emoji} no one failed their quota".format(
                green_emoji=self.config.green_tick_emote
            )
            quota_fail_embed.color = 0x38ff48
        else:
            quota_fail_embed.title = "{red_emoji} some staff failed their quota".format(
                red_emoji=self.config.red_tick_emote
            )
            quota_fail_embed.color = 0xff451c

        event.msg.reply("Quota check:", embed=quota_fail_embed)

    @Plugin.command("progress", "[staff:user]", group="quota", level=0)
    def quota_progress(self, event, staff=None):
        if staff is None:
            staff = event.msg.member

        if not isinstance(staff, GuildMember):
            try:
                staff = self.client.api.guilds_members_get(self.config.master_guild_id, staff.id)
            except APIException:
                event.msg.reply(":no_entry_sign: that person isn't on this server.")
                return

        if self.config.staff_role_id not in staff.roles:
            event.msg.reply(":no_entry_sign: you are not a staff member")
            return

        base = self.bot.plugins["BasePlugin"]
        year = datetime.datetime.now().date().isocalendar()[0]
        week = datetime.datetime.now().date().isocalendar()[1]
        is_sunday = (datetime.datetime.now().weekday() + 1) % 7
        if is_sunday == 0:
            week += 1
        quota_name = "{year}-{week}_staff-quota".format(
            year=year,
            week=week
        )

        quota = base.get_giveaway(quota_name, StaffQuota)

        if quota is None:
            event.msg.reply(":no_entry_sign: there is currently no quota this week.")
            return

        required = quota.messages_required
        participant = base.get_participant(quota.mongodb_id, staff.id, MessagesParticipant)[1]

        if participant is None:
            event.msg.reply(":no_entry_sign: you simply do not exist (send a few messages so the bot "
                            "can register you)")
            return

        messages = participant.message_count

        event.msg.reply("{emote} {pronoun} have **{messages}** / **{requirement}**".format(
            emote=self.config.red_tick_emote if messages < required else self.config.green_tick_emote,
            messages=str(messages),
            requirement=str(required),
            pronoun="you" if staff.id == event.msg.member.id else "they"
        ))
