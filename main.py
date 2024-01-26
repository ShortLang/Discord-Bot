import asyncio
import os
import subprocess
import discord
import platform
import docker
import requests
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env

client = docker.from_env()
image, build_logs = client.images.build(path=".", tag="shortlang_image", rm=True)


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
    

@bot.event
async def on_ready():
    await bot.load_extension("jishaku")
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def run(ctx, *, code: str):
    """Runs a block of ShortLang code"""

    if ctx.author.id != 655020762796654592:
        return await ctx.reply("You are not allowed to use this command.")

    code = code.replace('```', '')

    try:
        # Build Docker image
        image, build_logs = client.images.build(path=".", tag="shortlang_image", rm=True)
        
        # Run Docker container with a timeout and create file with code
        container = client.containers.run("shortlang_image", f"echo '{code}' | shortlang", detach=True, stderr=True)

        # Wait for the container to finish execution with a timeout
        result = container.wait(timeout=5)

        # If the container didn't finish execution within the timeout, stop it
        if result['StatusCode'] != 0:
            container.stop()
            
        # Fetch the stdout and stderr
        stdout = container.logs(stdout=True, stderr=False).decode()
        stderr = container.logs(stdout=False, stderr=True).decode()

        # Create the embed
        embed = discord.Embed(color=discord.colour.parse_hex_number("8080FF"))

        if len(stdout) != 0:
            output = f"```\n{stdout[:1500]}\n```"
        else:
            output = "*No output.*"

        embed.add_field(name="Program Output", value=output, inline=False)

        if len(stderr) != 0:
            embed.add_field(name="Compiler output", value=f"```\n{stderr[:500]}\n```", inline=False)
            embed.color = discord.colour.parse_hex_number("FF0000")

        await ctx.reply(embed=embed)

    except requests.exceptions.ConnectionError:
        await ctx.reply("The program took too long to execute.")

bot.run(os.getenv("DISCORD_TOKEN"))
