from disco.bot import Plugin, Config
import random


class ExtraPluginConfig(Config):
        
    cat_ids = [
        116757237262843906, #Poptart
        137919409644765184, #Jess
        150662786257518592, #Zach
        210118905006522369, #Ori 
        303502679089348608, #1A3
        390906358259777536  #CustomName
    ]

    cat_should_ping = True
    
    hug_phrases = [
        "<@{a}> gave <@{b}> a big big hug!",
        "With a great big hug from <@{a}>\nand a gift from me to you\nWon't you say you love me too <@{b}>?",
        "<@{a}> dabbed on <@{b}> haters and gave them a hug.",
        "<@{b}> unexpectedly received a big hug from <@{a}>",
        "<@{a}> reached out their arms, wrapped them around <@{b}> and gave them a giant hug!"
    ]
    fight_phrases = [
        "<@{a}> fought with <@{b}> with a large fish.",
        "<@{a}> tried to fight <@{b}>, but it wasn't very effective!",
        "<@{a}> fought <@{b}>, but they missed.",
        "<@{a}> fought <@{b}> with a piece of toast.",
        "<@{a}> and <@{b}> are fighting with a pillow.",
        "<@{a}> aimed but missed <@{b}> by an inch.",
        "<@{b}> got duck slapped by <@{a}>",
        "<@{a}> tried to dab on <@{b}> but they tripped, fell over, and now they need @ someone",
        "<@{b}> was saved from <@{a}> by wumpus' energy!",
        "Dabbit dabbed on <@{b}> from a request by <@{a}>!",
        "CustomName banned <@{a}> for picking a fight with <@{b}>!",
        "<@{a}> joined the game.\n<@{a}>: That's not very cash money of you.\n<@{b}>: What\nCONSOLE: <@{b}> was banned by an operator.\n<@{b}> left the game.",
        "<@{b}> tied <@{a}>’s shoelaces together, causing them to fall over.",
        "You are the Chosen One <@{a}>. You have brought balance to this world. Stay on this path, and you will do it again for the galaxy. But beware your heart said master <@{b}>",
        "<@{a}> used 'chat flood'. It wasn't very effective, so <@{b}> muted them."
    ]

    pat_ori_record = 4678
    pat_records = {}
    pat_ping_records = {}

@Plugin.with_config(ExtraPluginConfig)
class ExtraPlugin(Plugin):
    
    @Plugin.command("hug", "<person:user>", level=0)
    def hug_command(self, event, person):
        event.msg.delete()

        if not person or person.id == 210118905006522369:
            return event.msg.reply(
                "<@{a}> gave SFE's mascot, <@210118905006522369>, a hug!".format(a=event.author.id)
            ) 
        else: 
            message = random.choice(self.config.hug_phrases)
            return event.msg.reply(message.format(
                a=str(event.msg.author.id),
                b=str(person.id)
            ))

    @Plugin.command("fight", "<person:user>", level=0)
    def fight_command(self, event, person):
        message = random.choice(self.config.fight_phrases)
        event.msg.reply(message.format(
            a=str(event.msg.author.id),
            b=str(person.id)
        ))

    @Plugin.command("source", level=0)
    def open_source(self, event):
        event.msg.reply("We are open-source! Go here to see the GitHub repo: https://github.com/brxxn/sfe-giveaways")

    @Plugin.command("help", level=0)
    def help(self, event):
        event.msg.reply("List of Commands: https://github.com/brxxn/sfe-giveaways/wiki/Commands")

    # @Plugin.command("nick", "[nick:string...] [member:snowflake]", level=0, aliases=["nickname", "name"])
    # def nick(self, event, nick, user):
    #     """Nickname command, as requested by Colin"""
    #     if nick and member:
    #         member.change_nickname(member, nick)
    #         return event.msg.reply(":ok_hand: You changed <@{a}>'s nickname to `{b}`.".format(a=member.id, b=nick))
    #     elif nick:
    #         event.member.change_nickname(event.member, nick)
    #         return event.msg.reply(":ok_hand: You changed your nickname to `{a}`.".format(a=nick))
    #     else:
    #         event.member.change_nickname(event.member, None)
    #         return event.msg.reply(":ok_hand: Removed your nickname.".format(a=nick))

    @Plugin.command("pat", "[fluff:user]", level=0)
    def pat(self, event, fluff=None):
        event.msg.delete()

        if not fluff or fluff.id == 210118905006522369:
            self.config.pat_ori_record += 1
            return event.msg.reply(
                "<@{a}> gave SFE's mascot, <@210118905006522369>, a pat! (`{b}`)"
                    .format(a=event.author.id, b=self.config.pat_ori_record)
            ) 
        elif fluff.id == event.author.id:
            return event.msg.reply(
                ":negative_squared_cross_mark: You can't pat yourself, you fool."
            )
        else:
            pat_amount = self.config.pat_records.get(fluff.id)
            if not pat_amount:
                pat_amount = 1
                self.config.pat_records[fluff.id] = 1

            self.config.pat_records[fluff.id] += 1

            if self.config.pat_ping_records.get(fluff.id) or self.config.pat_ping_records.get(fluff.id) == None:
                return event.msg.reply(
                    "<@{a}> gave <@{b}> a pat! (`{c}`)"
                        .format(a=event.author.id, b=fluff.id, c=pat_amount)
                )
            else:
                return event.msg.reply(
                    "<@{a}> gave {b} a pat! (`{c}`)"
                        .format(a=event.author.id, b=fluff.tag, c=pat_amount)
                )

    @Plugin.command("patping", "<ping:int>", level=0)
    def patping(self, event, ping):
        if ping == 2:
            self.config.pat_ping_records[event.author.id] = True
            return event.msg.reply(":ok_hand: Enabled pat pings.")
        elif ping == 1:
            self.config.pat_ping_records[event.author.id] = False
            return event.msg.reply(":ok_hand: Disabled pat pings.")
        else:
            return event.msg.reply(":negative_squared_cross_mark: Expecting 1-2.")

    @Plugin.command("poptart", "[ping:int]", level=0, aliases=["cat"])
    def poptart(self, event, ping=None):
        """This is the poptart command - Given to poptart for most messages in a giveaway."""
        
        event.msg.delete()
        if ping and event.author.id == 116757237262843906:
            if ping == 1:
                self.config.cat_should_ping = False
                event.msg.reply(":ok_hand: Disabled pings. Enjoy your day, you fine cat.")
                return
            elif ping == 2:
                self.config.cat_should_ping = True
                event.msg.reply(":ok_hand: Enabled pings. Enjoy your day, you fine cat.")
                return
            else:
                return event.msg.reply(":negative_squared_cross_mark: Expecting 1-2.")
        
        if event.author.id not in self.config.cat_ids:
            return
        
        if self.config.cat_should_ping:
            event.msg.reply("**PSA: <@116757237262843906> is the coolest person here.**")
        else:
            event.msg.reply("**PSA: Cat is the coolest person here.**")
