# Grafana-only setup

Want to use the bot? Don't care about giveaways? Well then, you can setup the bot in *grafana only* mode. By using a simple technique of disabling 
all of the other plugins, you can make this easy peasy.

## Introduction

We use a full setup over on our main Discord server, [SFE](https://discord.gg/sfe), and it allows us to track member counts and messages sent per minute. It
can be used to determine active vs. idle times and other things like that. We will be adding more to this soon.

## Requirements

* have ports `3000`, `9090`, and `9091` open and available for use
* like any server that has at least 512mb of ram (i made that number up)
* Python & pip
* Git (you gotta install it somehow)

## Install grafana

You can just [go over here](https://grafana.com/grafana/download) to install grafana. Remember where you put the folder, it will be helpful later.

## Install prometheus

This requires a little more setup. First, download it [over here](https://prometheus.io/download). Then set your `prometheus.yml` file to:

```yml
# my global config
global:
  scrape_interval:     15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
  evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
  # scrape_timeout is set to the global default (10s).

# Alertmanager configuration
alerting:
  alertmanagers:
  - static_configs:
    - targets:
      # - alertmanager:9093

# Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
    - targets: ['localhost:9090']
      labels:
        group: 'production'
  - job_name: 'bot'
    static_configs:
      - targets: ['localhost:9091']
        labels:
          group: 'bot'
```

## Setup the config

Copy `example-grafana-only-config.json` to `config.json` and insert your token in there (oh yea you should probably create a bot and add it to your server).

You will need to make a folder called `config`. In this folder, put `grafana.json`. In there, you should have a setup like this:

```json
{
    "prometheus_port": "9091",
    "master_guild_id": 0
}
```

**REPLACE THE 0 WITH YOUR GUILD ID**, don't put it in quotes. It might mess something up.

## Start the bot

Note that the command line for using python may be different, but you can normally use `python -m disco.cli --config=config.json` if you didn't do anything super bad.

## Start grafana and prometheus

Use the `grafana-server` located in the binary files of the download (it's `grafana-server.exe` on windows). Use the `prometheus` server tool (it's `prometheus.exe` on windows).

## The good part

Go and head on over to port 3000 on your server once you've launched all the servers. Now, create an admin account. Your credentials don't really matter, as the bot doesn't
login to Grafana directly. Go ahead and create a Prometheus data source with the URL of `http://localhost:9090`. Now, go to the Dashboards icon > Manage. Click on `Import` and
copy the content from `grafana/template-dashboard.json` into the JSON section of the import page. Import it, and you should be good to go. If you have any questions, create an 
issue or DM me (brxxn#1337).

## Updating

Currently, you are required to manually perform updates. I'm working on a CI solution, but it might take a while.

## Known Issues

During downtime or when the bot is first starting up, all grafana counts are set to 0.