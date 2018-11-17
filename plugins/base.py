from disco.bot import Plugin, Config
from disco.api.http import APIException
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from types.giveaway import Giveaway
from types.participant import Participant
import random

class BasePluginConfig(Config):

    database_host = "localhost"
    database_port = 27017

    database_username = "sfegiveaways"
    database_password = "password" # This should be changed in the base.json config file.
    database_name = "giveaways"

    giveaway_permissions_role = 0
    master_guild_id = 0


@Plugin.with_config(BasePluginConfig)
class BasePlugin(Plugin):
    
    def load(self, ctx):
        """
        Base plugin for giveaways.
        """
        super(BasePlugin, self).load(ctx)
        self.mongo_client = MongoClient(
            self.config.database_host,
            self.config.database_port,
            username=self.config.database_username,
            password=self.config.database_password
        )
        self.database_enabled = False
        # Check connection to database.
        try:
            self.mongo_client.admin.command("ismaster")
            self.database_enabled = True
        except ConnectionFailure:
            print("--------- failed to connect to database. ---------")
            raise
        
        self.mongo_database = self.mongo_client[self.config.database_name]
        self.giveaways = self.mongo_database.get_collection("giveaways")
        self.users = self.mongo_database.get_collection("users")
        self.participants = self.mongo_database.get_collection("participants")

    @Plugin.command("databasestatus")
    def ping(self, event):
        event.msg.reply("Database status: *{status}*".format(
            status = "online" if self.database_enabled else "offline - bot will not function properly"
        )).after(10).delete()
    
    def get_all_giveaways(self):
        all_giveaways = []
        for giveaway_obj in self.giveaways.find({}):
            all_giveaways.append(Giveaway.from_database_object(giveaway_obj))
        return all_giveaways

    def get_giveaways(self, **kwargs):
        giveaways = []
        for giveaway_obj in self.giveaways.find(kwargs):
            giveaways.append(Giveaway.from_database_object(giveaway_obj))
        return giveaways
    
    def get_participant(self, giveaway_name, user_id):
        participant = self.participants.find_one({
            "giveaway_name": giveaway_name,
            "user_id": user_id
        })
        return (participant["_id"], Participant.from_database_object(participant))
    
    def get_participants_in_giveaway(self, giveaway_name):
        participant_objects = self.participants.find({
            "eligible": True,
            "blacklisted": False,
            "giveaway": giveaway_name
        })
        participants = []
        for participant_obj in participant_objects:
            participants.append(Participant.from_database_object(participant_obj))
        return participants
    
    def get_giveaway(self, giveaway_name):
        giveaway = self.giveaways.find_one({"name": giveaway_name})
        if giveaway is not None:
            giveaway = Giveaway.from_database_object(giveaway)
        return giveaway

    @Plugin.command("active")
    def active_giveaways(self, event):
        # TODO permissions
        message = "Active giveaways:\n\n"
        for giveaway in self.get_all_giveaways():
            if giveaway.active:
                message += "- {name}\n".format(
                    name = giveaway.name
                )
        event.msg.reply(message)
    
    @Plugin.command("pick", "<giveaway_name:str>")
    def end_giveaway(self, event, giveaway_name):
        # TODO permissions
        giveaway = self.get_giveaway(giveaway_name)
        participants = self.get_participants_in_giveaway(giveaway_name)
        if giveaway.pick_random:
            rand_start = 0
            rand_end = len(participants) - 1

            winner = participants[random.randint(rand_start, rand_end)]

            event.msg.reply("<@{user_id}> is the winner of **{giveaway_name}**.".format(
                user_id=str(winner.user_id),
                giveaway_name=giveaway.name
            ))
        else:
            event.msg.reply(":no_entry_sign: random mode isn't enabled on this giveaway.")
