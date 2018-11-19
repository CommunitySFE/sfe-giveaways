from disco.bot import Plugin, Config
import random


class HugFightConfig(Config):

    hug_phrases = [
        "<@{a}> gave <@{b}> a big big hug!"
    ]
    fight_phrases = [
        "<@{a}> fought with <@{b}> with a large fish.",
        "<@{a}> tried to fight <@{b}>, but it wasn't very effective",
        "<@{a}> fought <@{b}>, but they missed.",
        "<@{a}> fought <@{b}> with a piece of toast",
        "<@{a}> and <@{b}> are fighting with a pillow"
    ]


@Plugin.with_config(HugFightConfig)
class HugFight(Plugin):

    @Plugin.command("hug", "<person:user>", level=0)
    def hug_command(self, event, person):
        message = random.choice(self.config.hug_phrases)
        event.msg.reply(message.format(
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
