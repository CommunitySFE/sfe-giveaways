from disco.bot import Plugin, Config
from disco.bot.command import CommandLevels

# Constants

MASTER_GUILD_ID = 360462032811851777
STAFF_GUILD_ID = 414250233493454862

GIVEAWAY_ROLE_ID = 514143013812043777
STAFF_GIVEAWAY_ROLE_ID = 514141790790746122


def get_level(bot, actor):
    global MASTER_GUILD_ID, STAFF_GUILD_ID, GIVEAWAY_ROLE_ID, STAFF_GIVEAWAY_ROLE_ID
    if actor.guild is None:
        # Don't allow any commands to be run.
        return -1

    if actor.guild.id == MASTER_GUILD_ID:
        if GIVEAWAY_ROLE_ID in actor.roles:
            return CommandLevels.ADMIN
        return CommandLevels.DEFAULT
    elif actor.guild.id == STAFF_GUILD_ID:
        if STAFF_GIVEAWAY_ROLE_ID in actor.roles:
            return CommandLevels.ADMIN
        return CommandLevels.DEFAULT
    else:
        return CommandLevels.DEFAULT


class PermissionsPluginConfig(Config):
    
    use_defaults = True
    master_guild = 0
    staff_guild = 0

    giveaway_role = 0
    staff_giveaway_role = 0


@Plugin.with_config(PermissionsPluginConfig)
class PermissionsPlugin(Plugin):

    def load(self, ctx):
        super(PermissionsPlugin, self).load(ctx)
        global MASTER_GUILD_ID, STAFF_GUILD_ID, GIVEAWAY_ROLE_ID, STAFF_GIVEAWAY_ROLE_ID
        if not self.config.use_defaults:
            MASTER_GUILD_ID = self.config.master_guild
            STAFF_GUILD_ID = self.config.staff_guild
            GIVEAWAY_ROLE_ID = self.config.giveaway_role
            STAFF_GIVEAWAY_ROLE_ID = self.config.staff_giveaway_role
