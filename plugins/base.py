from disco.bot import Plugin, Config
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from types.giveaway import Giveaway

class BasePluginConfig(Config):

    database_host = "localhost"
    database_port = 27017

    database_username = "sfegiveaways"
    database_password = "password" # This should be changed in the base.json config file.
    database_name = "giveaways"


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

    @Plugin.command("active")
    def active_giveaways(self, event):
        message = "Active giveaways:\n\n"
        for giveaway in self.get_all_giveaways():
            if giveaway.active:
                message += "- {name}\n".format(
                    name = giveaway.name
                )
        event.msg.reply(message)