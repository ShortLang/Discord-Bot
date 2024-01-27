# ShortLang Discord Bot
## About
This bot allows you to run [ShortLang](https://github.com/ShortLang/ShortLang) code right in Discord.
ShortLang is a programming language where the syntax is meant to be as short as possible.
It is a simple language that is easy to learn and use.

The bot creates a new Docker container for each program that is run,
so you don't have to worry about someone nuking your PC.

## Usage
To use the bot, you can either join the ShortLang Discord server [here](https://discord.gg/9Q6JZuY) or host it yourself.
Please refer to the [installation](#installation) section for more information.

## Installation
To install the bot, you will need to have Docker and Python installed.
You will also need to create a Discord bot and get its token.
You can find instructions on how to do that [here](https://discordpy.readthedocs.io/en/latest/discord.html).

Once you have the bot token, you can run the following commands to install the bot:
```bash
git clone https://github.com/ShortLang/Discord-Bot
cd Discord-Bot
python3 -m pip install -r requirements.txt
```

After that,
you will need to rename the `example.env` file to `.env` and replace the `DISCORD_TOKEN` value with your bot token.

Before running, you need to place a linux executable of the ShortLang compiler in the root folder of the bot.
You can either compile it yourself
or download a precompiled version from the [releases](https://github.com/ShortLang/ShortLang/releases) page.
Please note that this bot can also be run on Windows, the linux executable is used inside a Docker container.

Once you have done that, you can run the bot with the following command:
```bash
python3 main.py
```

Remember to have Docker running when you run the bot or else it will not work.