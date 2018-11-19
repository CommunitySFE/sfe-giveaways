from disco.bot import Plugin, Config
from disco.api.http import APIException


class RewardsPluginConfig(Config):

    master_guild_id = 0


@Plugin.with_config(RewardsPluginConfig)
class RewardsPlugin(Plugin):

    @Plugin.command("rolereward", "<role_id:snowflake> <giveaway_name:str...>", group="giveaway", level=100)
    def command_role_reward(self, event, role_id, giveaway_name):
        base = self.bot.plugins["BasePlugin"]
        giveaway = base.get_giveaway(giveaway_name)
        if giveaway is None:
            event.msg.reply(":no_entry_sign: could not find giveaway.")
            return
        guild = self.client.api.guilds_get(str(self.config.master_guild_id))
        if role_id not in guild.roles:
            event.msg.reply(":no_entry_sign: invalid role ID")
            return

        participants = base.get_participants_in_giveaway(giveaway.name)
        if participants is None:
            event.msg.reply(":no_entry_sign: no participants in this giveaway.")
            return
        message = event.msg.reply(":gem: Loading... (this may take a while depending on how many people "
                                  "participated in the giveaway)")
        for participant in participants:
            try:
                participant_user = self.client.api.guilds_members_get(self.config.master_guild_id, participant.user_id)
            except APIException:
                continue
            if role_id in participant_user.roles:
                continue
            try:
                participant_user.add_role(role_id)
            except APIException:
                message.edit(":no_entry_sign: I don't have permission to give that role.")
                return
        message.edit(":ok_hand: gave roles to {participant_count} participants".format(
            participant_count=len(participants)
        ))
