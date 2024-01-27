import os

import asyncio
import discord
import docker
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
            allowed_mentions=discord.AllowedMentions(
                roles=False, users=False, everyone=False),
        )

    async def is_owner(self, user: discord.User):
        return user.id == 655020762796654592

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """The event triggered when an error is raised while invoking a command."""
        try:
            await ctx.reply(str(error))
        except:
            print(error)


intents = discord.Intents.default()
intents.message_content = True
bot = MyBot(intents=intents)


class CustomHelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return f'{command.qualified_name} {command.signature}'

    async def send_bot_help(self, _mapping):
        embed = discord.Embed(title='Commands', color=discord.Color.blue(),
                              description="For help with a specific command, type `-help <command>`")
        for command in self.context.bot.commands:
            if command.qualified_name == "jishaku":
                continue
            if not command.hidden:
                embed.add_field(name=f'{self.get_command_signature(command)}',
                                value=f"```{command.help or 'No description'}```", inline=False)
        await self.get_destination().send(embed=embed)


bot.help_command = CustomHelpCommand()


def run_container(code):
    container = client.containers.run("shortlang_image", [
                                      "bash", "-c", f"echo '{code}' | shortlang -s"], detach=True, stderr=True)
    try:
        result = container.wait(timeout=5)
    except:
        return "Error: The program took too long to execute."
    if result['StatusCode'] != 0:
        container.stop()
    return container


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

    # Run the container in a separate thread to avoid blocking
    loop = asyncio.get_event_loop()
    container = await loop.run_in_executor(None, run_container, code)

    if isinstance(container, str):
        # If the container returned a string, it's an error message
        embed = discord.Embed(color=discord.colour.parse_hex_number("FF0000"))
        embed.add_field(name="Error Output", value="```" + container + "```", inline=False)
        await ctx.message.remove_reaction('⏳', bot.user)
        return await ctx.reply(embed=embed)

    # Fetch the stdout and stderr
    stdout = container.logs(stdout=True, stderr=False).decode()
    stderr = container.logs(stdout=False, stderr=True).decode()

    # Create the embed
    embed = discord.Embed(color=discord.colour.parse_hex_number("8080FF"))
    output = f"```{stdout[:1010]}```" if len(stdout) != 0 else "*No output.*"
    embed.add_field(name="Program Output", value=output, inline=False)

    if len(stderr) != 0:
        embed.add_field(name="Error Output", value=f"```{stderr[:1010]}```", inline=False)
        embed.color = discord.colour.parse_hex_number("FF0000")

    await ctx.reply(embed=embed)
    await ctx.message.remove_reaction('⏳', bot.user)


bot.run(os.getenv("DISCORD_TOKEN"))
