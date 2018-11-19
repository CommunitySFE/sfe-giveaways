from disco.bot import Plugin, Config
from disco.types.message import MessageEmbed
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from structures.exception import GiveawayResultFailure
from structures.giveaway import Giveaway
from structures.participant import Participant
import structures.constants
import random
import time


class BasePluginConfig(Config):

    database_host = "localhost"
    database_port = 27017

    database_username = "sfegiveaways"
    database_password = "password"
    database_name = "giveaways"

    # Set to False in debug environments
    use_authentication = True

    master_guild_id = 360462032811851777


@Plugin.with_config(BasePluginConfig)
class BasePlugin(Plugin):
    
    def load(self, ctx):
        """
        Base plugin for giveaways.
        """
        super(BasePlugin, self).load(ctx)
        if self.config.use_authentication:
            self.mongo_client = MongoClient(
                self.config.database_host,
                self.config.database_port,
                username=self.config.database_username,
                password=self.config.database_password
            )
        else :
            self.mongo_client = MongoClient(self.config.database_host, self.config.database_port)
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

    @Plugin.command("databasestatus", level=100)
    def ping(self, event):
        event.msg.reply("Database status: *{status}*".format(
            status="online" if self.database_enabled else "offline - bot will not function properly"
        )).after(10).delete()
    
    def get_all_giveaways(self):
        """
        Returns an array of all Giveaway objects
        """
        all_giveaways = []
        for giveaway_obj in self.giveaways.find({}):
            all_giveaways.append(Giveaway.from_database_object(giveaway_obj))
        return all_giveaways

    def get_giveaways(self, cls, **kwargs):
        """
        Get giveaways that meet the specific requirements defined in keyword arguments.

        Returns an array of Giveaway objects.
        """
        giveaways = []
        for giveaway_obj in self.giveaways.find(kwargs):
            giveaways.append(cls.from_database_object(giveaway_obj))
        return giveaways
    
    def get_participant(self, giveaway_id, user_id, cls):
        """
        Get participants by giveaway name and userid.
        """
        participant = self.participants.find_one({
            "giveaway": giveaway_id,
            "user_id": user_id
        })
        if participant is None:
            return None, None
        return participant["_id"], cls.from_database_object(participant)
    
    def create_participant(self, cls, **kwargs):
        participant = cls.from_database_object(kwargs)
        self.participants.insert_one(participant.to_database_object())
    
    def update_participant(self, database_id, **kwargs):
        self.participants.update_one({
            "_id": database_id
        }, {
            "$set": kwargs
        })
    
    def get_participants_in_giveaway(self, giveaway_name):
        giveaway = self.get_giveaway(giveaway_name)
        participant_objects = self.participants.find({
            "eligible": True,
            "blacklisted": False,
            "giveaway": giveaway.mongodb_id
        })
        participants = []
        for participant_obj in participant_objects:
            participants.append(Participant.from_database_object(participant_obj))
        return participants

    def get_staff_in_quota(self, quota_name, cls=Participant):
        giveaway = self.get_giveaway(quota_name)
        if giveaway is None:
            return None
        participant_objects = self.participants.find({
            "giveaway": giveaway.mongodb_id
        })
        participants = []
        for participant_obj in participant_objects:
            participants.append(cls.from_database_object(participant_obj))
        return participants

    def get_giveaway(self, giveaway_name):
        giveaway = self.giveaways.find_one({"name": giveaway_name})
        if giveaway is not None:
            giveaway = Giveaway.from_database_object(giveaway)
        return giveaway
    
    def create_giveaway(self, cls, **kwargs):
        giveaway = cls.from_database_object(kwargs)
        giveaway_object = self.giveaways.insert_one(giveaway.to_database_object())
        return giveaway, giveaway_object
    
    def update_giveaway(self, giveaway_id, **kwargs):
        self.giveaways.update_one({
            "_id": giveaway_id
        }, {
            "$set": kwargs
        })

    def pick_giveaway(self, giveaway):
        participants = self.get_participants_in_giveaway(giveaway.name)
        if giveaway.pick_random:
            if len(participants) <= 1:
                raise GiveawayResultFailure("not enough participants.")
            rand_start = 1
            rand_end = len(participants)

            winner = participants[random.randint(rand_start, rand_end) - 1]

            return winner.user_id
        else:
            raise GiveawayResultFailure("random mode isn't enabled on this giveaway.")

    @Plugin.command("active", group="giveaway", level=0)
    def active_giveaways(self, event):
        giveaways = self.get_all_giveaways()
        active_giveaways = []
        for giveaway in giveaways:
            if giveaway.active and giveaway.giveaway_type != "staff quota":
                active_giveaways.append(giveaway)
        if len(active_giveaways) == 0:
            event.msg.reply(":no_entry_sign: there are no active giveaways at this time.")
            return
        embed = MessageEmbed()
        embed.title = "Active Giveaways"
        embed.description = "This is a list of all active giveaways on the server."
        embed.color = 0x7289da
        for active_giveaway in active_giveaways:
            embed.add_field(
                name=active_giveaway.name,
                value="Giveaway type: {type}".format(type=active_giveaway.giveaway_type)
            )
        event.msg.reply("Active giveaways:", embed=embed)
    
    @Plugin.command("pick", "<giveaway_name:str...>", group="giveaway", level=100)
    def command_pick_giveaway(self, event, giveaway_name):
        giveaway = self.get_giveaway(giveaway_name)
        if giveaway is None:
            event.msg.reply(":no_entry_sign: giveaway does not exist.")
            return
        try:
            winner = self.pick_giveaway(giveaway)
        except GiveawayResultFailure as failure:
            event.msg.reply(failure.get_error_message())
            return
        event.msg.reply(":tada: <@{winner}> won the giveaway **{giveaway}**!".format(
            winner=winner,
            giveaway=giveaway.name
        ))
    
    @Plugin.command("autopick", "<time_value:int> <time_measurement:str> <giveaway_name:str...>", group="giveaway", level=100)
    def autopick_giveaway(self, event, time_value, time_measurement, giveaway_name):
        if not time_measurement.lower() in structures.constants.TIME_MEASUREMENTS:
            event.msg.reply(":no_entry_sign: unknown time measurement. use `seconds`, `minutes`, `hours`, or `days`.")
            return
        measurement = structures.constants.TIME_MEASUREMENTS[time_measurement.lower()]
        pick_time = time.time() + (time_value * measurement)
        giveaway = self.get_giveaway(giveaway_name)
        if giveaway is None:
            event.msg.reply(":no_entry_sign: could not find giveaway with that name.")
            return
        self.update_giveaway(giveaway.mongodb_id, autopick=True, autopick_time=pick_time)
        event.msg.reply(":ok_hand: giveaway winner will be automatically picked.")

    @Plugin.command("toggleactive", "<giveaway_name:str...>", group="giveaway", level=100)
    def toggle_active(self, event, giveaway_name):
        giveaway = self.get_giveaway(giveaway_name)
        if giveaway is None:
            event.msg.reply(":no_entry_sign: could not find giveaway.")
            return
        self.update_giveaway(giveaway.mongodb_id, active=not giveaway.active)
        event.msg.reply(":ok_hand: {giveaway} is {no_longer}active".format(
            giveaway=giveaway_name,
            no_longer="no longer " if giveaway.active else ""
        ))

    @Plugin.command("togglerandom", "<giveaway_name:str...>", group="giveaway", level=100)
    def toggle_random(self, event, giveaway_name):
        giveaway = self.get_giveaway(giveaway_name)
        if giveaway is None:
            event.msg.reply(":no_entry_sign: could not find giveaway.")
            return
        self.update_giveaway(giveaway.mongodb_id, pick_random=not giveaway.pick_random)
        event.msg.reply(":ok_hand: {giveaway} is {no_longer}random".format(
            giveaway=giveaway_name,
            no_longer="no longer " if giveaway.pick_random else ""
        ))

    @Plugin.command("cleanup", group="giveaway", level=100)
    def cleanup(self, event):
        inactive_giveaways = self.get_giveaways(Giveaway, active=False)
        for giveaway in inactive_giveaways:
            self.participants.delete_many({
                "giveaway": giveaway.mongodb_id
            })
            self.giveaways.delete_one({
                "_id": giveaway.mongodb_id
            })
        event.msg.reply(":ok_hand: cleanup successful.")
