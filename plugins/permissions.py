from disco.bot.command import CommandLevels

# Constants

MASTER_GUILD_ID = 360462032811851777
STAFF_GUILD_ID = 414250233493454862

GIVEAWAY_ROLE_ID = 0
STAFF_GIVEAWAY_ROLE_ID = 0

global MASTER_GUILD_ID, STAFF_GUILD_ID, GIVEAWAY_ROLE_ID, STAFF_GIVEAWAY_ROLE_ID

class CommandLevelGetter:

    def __call__(self, actor):
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
