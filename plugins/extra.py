from disco.bot import Plugin, Config
import random
import time


class ExtraPluginConfig(Config):

    cat_ids = [
        116757237262843906,  # Poptart
        137919409644765184,  # Jess
        150662786257518592,  # Zach
        156670353282695168,  # Critiql
        210118905006522369,  # Ori
        210540648128839680,  # Guffuffle
        249462738257051649,  # Lost
        303502679089348608,  # 1A3
        390906358259777536,  # CustomName
        436481695617777665   # Tiller
    ]

    cat_should_ping = True

    cat_noun = "coolest cat"

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

    pat_dissipation_count = 0
    pat_records = {}
    pat_ping_records = {}
    noot_record = 0

    custom_commands = [{
        'name': 'diditworkandwhatdiditcost',
        'content': 'yes, it did, and it cost like under 30 minutes of your time.'
    }]
    donator_plus_role = 627562670303739905


@Plugin.with_config(ExtraPluginConfig)
class ExtraPlugin(Plugin):

    def load(self, ctx):
        super(ExtraPlugin, self).load(ctx)
        self.base_plugin = self.bot.plugins['BasePlugin']
        self.custom_command_db = self.base_plugin.custom_commands
        self.custom_commands = []
        self.command_cooldowns = dict()
        self.reload_custom_commands()
    
    def reload_custom_commands(self):
        # Reset the custom command storage
        self.custom_commands = []
        # Fetch active custom commands from database
        self.custom_commands = self.base_plugin.get_active_custom_commands()
        # print("Custom commands reloaded.")

    def is_donator(self, member):
        return self.config.donator_plus_role in member.roles

    @Plugin.command("create", "<name:str...>", group="cc", level=0)
    def create_command(self, event, name):
        if event.msg.guild is None:
            return

        if not self.is_donator(event.msg.member):
            event.msg.reply(':no_entry_sign: Sorry, but you must have Donator+ to use this command. Please get Donator+ at ' +
                '<https://www.paypal.com/pools/c/8iCBNxzoRJ> to get custom command permissions for SFE.')
            return

        if len(name) <= 2:
            event.msg.reply(':no_entry_sign: please make a longer name.')
            return

        previous_custom_command = self.custom_command_db.find_one({
            '$or': [{
                'name': name
            }, {
                'author': event.msg.author.id
            }]
        })

        if previous_custom_command is not None:
            event.msg.reply(':no_entry_sign: you either already have a custom command or have created a custom command before.')
            return
        
        self.custom_command_db.insert_one({
            'active': False,
            'name': name,
            'content': '[content not set]',
            'author': event.msg.author.id
        })

        event.msg.reply(':ok_hand: custom command created successfully. you can change the content using `.cc setcontent <content>`')
    
    @Plugin.command("setcontent", "<content:str...>", group="cc", level=0)
    def set_command_content(self, event, content):
        if event.msg.guild is None:
            return

        if not self.is_donator(event.msg.member):
            event.msg.reply(':no_entry_sign: Sorry, but you must have Donator+ to use this command. Please get Donator+ at ' +
                '<https://www.paypal.com/pools/c/8iCBNxzoRJ> to get custom command permissions for SFE.')
            return

        if len(content) <= 2:
            event.msg.reply(':no_entry_sign: you need at least 3 characters of content.')
            return

        previous_custom_command = self.custom_command_db.find_one({
            'author': event.msg.author.id
        })

        if previous_custom_command is None:
            event.msg.reply(':no_entry_sign: you don\'t have an inactive custom command. you can create one using `.cc create <name>`.')
            return
        
        if '@everyone' in content or '@here' in content:
            event.msg.reply(':no_entry_sign: do not attempt to mention everyone in your command content.')
            return
        
        self.custom_command_db.update_one({
            '_id': previous_custom_command['_id']
        }, {
            '$set': {
                'content': content
            }
        })

        if not previous_custom_command['active']:
            event.msg.reply(':ok_hand: content updated. for your command to go live, you\'ll have to ask for approval.')
        else:
            self.reload_custom_commands()
            event.msg.reply(':ok_hand: command content updated successfully.')

    @Plugin.command('setactive', '<name:str...>', group='cc', level=100)
    def set_command_active(self, event, name):
        custom_command = self.custom_command_db.find_one({
            'name': name
        })

        if custom_command is None:
            event.msg.reply(':no_entry_sign: could not find custom command with that name.')
            return
        
        self.custom_command_db.update_one({
            '_id': custom_command['_id']
        }, {
            '$set': {
                'active': True
            }
        })

        self.reload_custom_commands()
        
        event.msg.reply(':ok_hand: command is now active.')
    
    @Plugin.command('blacklist', '<user:user>', group='cc', level=0)
    def blacklist_user_from_command(self, event, user):
        custom_command = self.custom_command_db.find_one({
            'author': event.msg.author.id
        })

        if custom_command is None:
            event.msg.reply(":no_entry_sign: you don't have a custom command.")
            return
        
        blacklist = []

        if custom_command.get('blacklisted_users') is not None:
            blacklist = custom_command['blacklisted_users']
        
        if user.id in blacklist:
            blacklist.remove(user.id)
        else:
            blacklist.append(user.id)

        self.custom_command_db.update_one({
            '_id': custom_command['_id']
        }, {
            '$set': {
                'blacklisted_users': blacklist
            }
        })

        self.reload_custom_commands()

        event.msg.reply(':ok_hand: blacklist toggled for {user} (`{id}`).'.format(user=str(user), id=user.id))
    
    @Plugin.command('whitelist', '<user:user>', group='cc', level=0)
    def whitelist_user_for_command(self, event, user):
        custom_command = self.custom_command_db.find_one({
            'author': event.msg.author.id
        })

        if custom_command is None:
            event.msg.reply(":no_entry_sign: you don't have a custom command.")
            return
        
        whitelist = []

        if custom_command['whitelisted_users'] is not None:
            if custom_command['whitelisted_users'] == 'all':
                event.msg.reply(':no_entry_sign: whitelist is not enabled. please enable it using `.cc togglewhitelist`.')
                return
            whitelist = custom_command['whitelisted_users']
        
        if user.id in whitelist:
            whitelist.remove(user.id)
        else:
            whitelist.append(user.id)

        self.custom_command_db.update_one({
            '_id': custom_command['_id']
        }, {
            '$set': {
                'whitelisted_users': whitelist
            }
        })

        self.reload_custom_commands()

        event.msg.reply(':ok_hand: whitelist toggled for {user} (`{id}`).'.format(user=str(user), id=user.id))
    
    @Plugin.command('togglewhitelist', group='cc', level=0)
    def toggle_command_whitelist(self, event):
        custom_command = self.custom_command_db.find_one({
            'author': event.msg.author.id
        })

        if custom_command is None:
            event.msg.reply(":no_entry_sign: you don't have a custom command.")
            return

        whitelist = None

        if custom_command.get('whitelisted_users') is None or type(custom_command.get('whitelisted_users')) == str:
            whitelist = [event.msg.author.id]
        else:
            whitelist = 'all'

        self.custom_command_db.update_one({
            '_id': custom_command['_id']
        }, {
            '$set': {
                'whitelisted_users': whitelist
            }
        })

        self.reload_custom_commands()

        event.msg.reply(':ok_hand: whitelist successfully toggled.')

    @Plugin.command('forcereload', group='cc', level=100)
    def force_custom_command_reload(self, event):
        self.reload_custom_commands()
        event.msg.reply(':ok_hand: custom commands reloaded.')
    
    @Plugin.command('delete', group='cc', level=0)
    def delete_custom_command(self, event):
        custom_command = self.custom_command_db.find_one({
            'author': event.msg.author.id
        })

        if custom_command is None:
            event.msg.reply(":no_entry_sign: you don't have a custom command.")
            return
        was_active = custom_command['active']
        self.custom_command_db.delete_one({
            '_id': custom_command['_id']
        })
        if was_active:
            self.reload_custom_commands()
        event.msg.reply(':ok_hand: custom command removed successfully.')
    
    @Plugin.command('forcedelete', '<name:str...>', group='cc', level=100)
    def force_delete_custom_command(self, event, name):
        custom_command = self.custom_command_db.find_one({
            'name': name
        })

        if custom_command is None:
            event.msg.reply(":no_entry_sign: couldn't find a custom command with that name.")
            return

        was_active = custom_command['active']
        self.custom_command_db.delete_one({
            '_id': custom_command['_id']
        })
        if was_active:
            self.reload_custom_commands()
        event.msg.reply(':ok_hand: custom command removed successfully.')

    @Plugin.command("hug", "[person:user]", level=0)
    def hug_command(self, event, person=None):
        event.msg.delete()

        if not person:
            return event.msg.reply(
                "<@{a}> tried to hug nobody, but the ***V O I D*** was unable to do anything, and could only stare back in return.".format(
                    a=event.author.id)
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
        event.msg.reply(
            "We are open-source! Go here to see the GitHub repo: https://github.com/brxxn/sfe-giveaways")

    @Plugin.command("help", level=0)
    def help(self, event):
        event.msg.reply(
            "List of Commands: https://github.com/brxxn/sfe-giveaways/wiki/Commands")

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

    @Plugin.listen("MessageCreate")
    def custom_command_event(self, event):
        if event.message.guild is None:
            return

        if event.message.author.bot:
            return
        
        if not event.message.content.startswith('.'):
            return
        
        for command in self.custom_commands:
            if command.get("name") is None or command.get("content") is None:
                print("WARNING: Custom commands must have a name and content value.")
                continue
            if not event.message.content.lower().startswith(".%s" % command.get("name").lower()):
                continue
            if command.get('whitelisted_users') is not None:
                if type(command.get('whitelisted_users')) is str:
                    if not command.get('whitelisted_users') == 'all':
                        break
                else:
                    if not event.message.author.id in command.get('whitelisted_users') and not event.message.member.permissions.can("ADMINISTRATOR"):
                        break
            if command.get('blacklisted_users') is not None:
                if event.message.author.id in command.get('blacklisted_users') and not event.message.member.permissions.can("ADMINISTRATOR"):
                    break
            content = command.get("content")
            command_name_length = len(command.get("name").split(" "))
            split_command = event.message.content.split(" ")
            for i in range(command_name_length - 1, len(split_command)):
                if '@everyone' in split_command[i] or '@here' in split_command[i]:
                    event.message.reply(":no_entry_sign: cannot mention everyone/here in command arguments.")
                    return
                content = content.replace("${%s}" % (i), split_command[i])
            if '${...}' in content:
                split_command.pop(0)
                content = content.replace('${...}', ' '.join(split_command))
                if '@everyone' in content or '@here' in content:
                    event.message.reply(":no_entry_sign: cannot mention everyone/here in command arguments.")
                    return
            if self.command_cooldowns.get(command.get('name'), 0) + 20 > time.time():
                event.message.add_reaction('⏱')
                return
            self.command_cooldowns[command.get('name')] = time.time()
            event.message.channel.send_message(content)

    @Plugin.command("pat", "[fluff:user]", level=0)
    def pat(self, event, fluff=None):
        event.msg.delete()

        if not fluff:
            self.config.pat_dissipation_count += 1
            return event.msg.reply(
                "<@{a}> tried to give nobody a pat, but the energy was dissipated into the ***V O I D.*** (`{b}` wasted pats)"
                .format(a=event.author.id, b=self.config.pat_dissipation_count)
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

            if self.config.pat_ping_records.get(fluff.id) or self.config.pat_ping_records.get(fluff.id) is None:
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

    @Plugin.command("poptart", "[ping:int] [noun:str...]", aliases=["cat"], level=0)
    def poptart(self, event, ping=None, noun=str):
        """This is the poptart command - Given to Poptart for most messages in a giveaway."""

        if ping and event.author.id == 116757237262843906:
            if ping == 1:
                event.msg.delete()
                self.config.cat_should_ping = False
                event.msg.reply(":ok_hand: Disabled pings. Enjoy your day, you fine cat.")
                return
            elif ping == 2:
                event.msg.delete()
                self.config.cat_should_ping = True
                event.msg.reply(":ok_hand: Enabled pings. Enjoy your day, you fine cat.")
                return
            elif ping == 3:
                if noun:
                    event.msg.delete()
                    self.config.cat_noun = noun
                    event.msg.reply(":ok_hand: Noun set to {a}. Enjoy your day, you fine cat.".format(
                        a=str(self.config.cat_noun)))
                else:
                    event.msg.reply(":negative_squared_cross_mark: Expecting a string.")
                return
            elif ping == 4:
                event.msg.delete()
                if "@everyone" in noun or "@here" in noun:
                    event.msg.reply("no can do")
                event.msg.reply("**PSA: {a}**".format(a=str(noun)))
                return
            elif ping == 5:
                event.msg.delete()
                if not noun.isdigit():
                    event.msg.reply(":no_entry_sign: invalid user id")
                    return
                cat_ids = self.config.cat_ids
                cat_ids.append(int(noun))
                self.config.cat_ids = cat_ids
                event.msg.reply(":ok_hand: added {user_id} to whitelisted cat IDs".format(user_id=noun))
            elif ping == 6:
                event.msg.delete()
                if not noun.isdigit():
                    event.msg.reply(":no_entry_sign: invalid user id")
                    return
                self.config.cat_ids.remove(int(noun))
                event.msg.reply(":ok_hand: removed {user_id} from whitelisted cat IDs".format(user_id=noun))
            else:
                return event.msg.reply(":negative_squared_cross_mark: Expecting 1-6.")

        if event.author.id not in self.config.cat_ids:
            return

        event.msg.delete()

        if self.config.cat_should_ping:
            event.msg.reply(
                "**PSA: <@116757237262843906> is the {a} here.**".format(a=str(self.config.cat_noun)))
        else:
            event.msg.reply(
                "**PSA: Cat is the {a} here.**".format(a=str(self.config.cat_noun)))
