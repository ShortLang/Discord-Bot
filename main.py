import os
import discord
import docker
import requests
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env

client = docker.from_env()
client.images.build(path=".", tag="shortlang_image", rm=True)


class MyBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or("-"),
            case_insensitive=True,
            intents=kwargs.pop("intents", discord.Intents.all()),
            allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False),
        )

    async def is_owner(self, user: discord.User):
        if user.id == 655020762796654592:
            return True
        else:
            return False
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """The event triggered when an error is raised while invoking a command."""
        await ctx.reply(str(error))


intents = discord.Intents.default()
intents.message_content = True
bot = MyBot(intents=intents)


class CustomHelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return f'{command.qualified_name} {command.signature}'

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title='Commands', color=discord.Color.blue(), description="For help with a specific command, type `-help <command>`")
        for command in self.context.bot.commands:
            if command.qualified_name == "jishaku": continue
            if not command.hidden:
                embed.add_field(name=f'{self.get_command_signature(command)}', value=f"```{command.help or 'No description'}```", inline=False)
        await self.get_destination().send(embed=embed)


bot.help_command = CustomHelpCommand()
    

@bot.event
async def on_ready():
    await bot.load_extension("jishaku")
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

    await bot.change_presence(activity=discord.Game(name="Use -help for usage!"))

@bot.command()
async def run(ctx, *, code: str = None):
    """Runs the given ShortLang code"""

    # Add a reaction to the message to indicate that the bot is processing the command
    await ctx.message.add_reaction('⏳')

    if ctx.message.attachments:
        # If a file was sent, download it and read its content
        file = await ctx.message.attachments[0].read()
        code = file.decode()
    else:
        # If no file was sent, use the provided code
        code = code.replace('```', '').replace("'", '"')

    # Run Docker container with a timeout and create file with code
    container = client.containers.run("shortlang_image", ["bash", "-c", f"echo '{code}' | shortlang"], detach=True, stderr=True)
    
    try:
        # Wait for the container to finish execution with a timeout
        result = container.wait(timeout=5)
    except requests.exceptions.ConnectionError:
        embed = discord.Embed(color=discord.colour.parse_hex_number("FF0000"))
        embed.add_field(name="Error Output", value="```Error: The program took too long to execute.```", inline=False)
        await ctx.message.remove_reaction('⏳', bot.user)
        return await ctx.reply(embed=embed)

    # If the container didn't finish execution within the timeout, stop it
    if result['StatusCode'] != 0:
        container.stop()

    # Fetch the stdout and stderr
    stdout = container.logs(stdout=True, stderr=False).decode()
    stderr = container.logs(stdout=False, stderr=True).decode()

    # Create the embed
    embed = discord.Embed(color=discord.colour.parse_hex_number("8080FF"))

    if len(stdout) != 0:
        output = f"```{stdout[:1010]}```"
    else:
        output = "*No output.*"

    embed.add_field(name="Program Output", value=output, inline=False)

    if len(stderr) != 0:
        embed.add_field(name="Error Output", value=f"```{stderr[:1010]}```", inline=False)
        embed.color = discord.colour.parse_hex_number("FF0000")

    await ctx.reply(embed=embed)
    await ctx.message.remove_reaction('⏳', bot.user)


bot.run(os.getenv("DISCORD_TOKEN"))
