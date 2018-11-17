from disco.bot import Plugin, Config
from disco.api.http import APIException
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from types.giveaway import Giveaway
from types.participant import Participant
import types.constants
import random
import time

class BasePluginConfig(Config):

    database_host = "localhost"
    database_port = 27017

    database_username = "sfegiveaways"
    database_password = "password" # This should be changed in the base.json config file.
    database_name = "giveaways"

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
        self.participants = self.mongo_database.get_collection("participants")

    @Plugin.command("databasestatus")
    def ping(self, event):
        event.msg.reply("Database status: *{status}*".format(
            status = "online" if self.database_enabled else "offline - bot will not function properly"
        )).after(10).delete()
    
    def get_all_giveaways(self):
        """
        Returns an array of all Giveaway objects
        """
        all_giveaways = []
        for giveaway_obj in self.giveaways.find({}):
            all_giveaways.append(Giveaway.from_database_object(giveaway_obj))
        return all_giveaways

    def get_giveaways(self, **kwargs):
        """
        Get giveaways that meet the specific requirements defined in keyword arguments.

        Returns an array of Giveaway objects.
        """
        giveaways = []
        for giveaway_obj in self.giveaways.find(kwargs):
            giveaways.append(Giveaway.from_database_object(giveaway_obj))
        return giveaways
    
    def get_participant(self, giveaway_name, user_id, cls):
        """
        Get participants by giveaway name and userid.


        """
        participant = self.participants.find_one({
            "giveaway_name": giveaway_name,
            "user_id": user_id
        })
        if participant is None:
            return (None, None)
        return (participant["_id"], cls.from_database_object(participant))
    
    def create_participant(self, **kwargs):
        participant = Participant.from_database_object(kwargs)
        self.participants.insert_one(participant.to_database_object())
    
    def update_participant(self, database_id, **kwargs):
        self.participants.update_one({
            "_id": database_id
        }, {
            "$set": kwargs
        })
    
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
    
    def create_giveaway(self, cls, **kwargs):
        giveaway = cls.from_database_object(kwargs)
        giveaway_object = self.giveaways.insert_one(giveaway)
        return (giveaway, giveaway_object)
    
    def update_giveaway(self, giveaway_id, **kwargs):
        self.giveaways.update_one({
            "_id": giveaway_id
        }, {
            "$set": kwargs
        })

    @Plugin.command("active", level=0)
    def active_giveaways(self, event):
        # TODO permissions
        message = "Active giveaways:\n\n"
        for giveaway in self.get_all_giveaways():
            if giveaway.active:
                message += "- {name}\n".format(
                    name = giveaway.name
                )
        event.msg.reply(message)
    
    @Plugin.command("pick", "<giveaway_name:str>", level=100)
    def end_giveaway(self, event, giveaway_name):
        giveaway = self.get_giveaway(giveaway_name)
        if giveaway is None:
            event.msg.reply(":no_entry_sign: giveaway does not exist.")
            return
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
    
    @Plugin.command("autopick", "<time_value:int> <time_measurement:str> <giveaway_name:str...>", level=100)
    def autopick_giveaway(self, event, time_value, time_measurement, giveaway_name):
        if not types.constants.TIME_MEASUREMENTS.has_key(time_measurement.lower()):
            event.msg.reply(":no_entry_sign: unknown time measurement. use `seconds`, `minutes`, `hours`, or `days`.")
            return
        measurement = types.constants.TIME_MEASUREMENTS[time_measurement.lower()]
        pick_time = time.time() + (time_value * measurement)
        giveaway = self.get_giveaway(giveaway_name)
        if giveaway is None:
            event.msg.reply(":no_entry_sign: could not find giveaway with that name.")
            return
        self.update_giveaway(giveaway.mongodb_id, autopick=True, autopick_time=pick_time)
        event.msg.reply(":ok_hand: giveaway winner will be automatically picked.")
