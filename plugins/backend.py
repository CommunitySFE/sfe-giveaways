from disco.bot import Plugin, PluginConfig

class BackendPluginConfig(PluginConfig):
    
    captcha_site_key = "0"


class BackendPlugin(Plugin):

    def load(self, ctx):
        super(BackendPlugin, self).load(ctx)
    

