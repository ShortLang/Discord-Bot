import asyncio
import os
import subprocess
import discord
import platform
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env

intents = discord.Intents.default()
intents.message_content = True
allowed_mentions = discord.AllowedMentions(roles=False, users=False, everyone=False)
bot = commands.Bot(command_prefix='-', intents=intents, allowed_mentions=allowed_mentions)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def run(ctx, *, code: str):
    """Runs a block of ShortLang code"""

    code = code.replace('```', '')
    with open("program.sl", "w") as f:
        f.writelines(code)

    command = "shortlang"
    if platform.system() == "Windows":
        command += ".exe"

    try:
        process = await asyncio.create_subprocess_shell(
            f"{command} program.sl",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            limit=4096  # Set a reasonable limit for the output
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5)

        if process.returncode is None:
            process.terminate()
            raise asyncio.TimeoutError("Process timed out.")

        # response = f"**Output:**\n```\n{stdout.decode()[:1500]}\n```\n**Error:**\n```\n{stderr.decode()}\n```"

        embed = discord.Embed(color=discord.colour.parse_hex_number("8080FF"))
        stdout = stdout.decode()

        if len(stdout) != 0:
            output = f"```\n{stdout.decode()[:1500]}\n```"
        else:
            output = "*No output.*"

        embed.add_field(name="Program Output", value=output, inline=False)
        stderr = stderr.decode()

        if len(stderr) != 0:
            embed.add_field(name="Compiler output", value=f"```\n{stderr[:500]}\n```", inline=False)
            embed.color = discord.colour.parse_hex_number("FF0000")

        await ctx.reply(embed=embed)

    except asyncio.TimeoutError:
        await ctx.reply("The process timed out.")


bot.run(os.getenv("DISCORD_TOKEN"))
