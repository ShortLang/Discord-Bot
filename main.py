import asyncio
import os
import re
import subprocess
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='-', intents=intents)

discord.AllowedMentions(everyone=False, roles=False, users=False)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def run(ctx, *, code: str):
    """Runs a block of shortlang code"""

    if ctx.author.id != 873410122616037456:
        return

    code = code.replace('```', '')
    print(f"code is: {code}")

    with open("tmp.sl", "w") as f:
        f.writelines(code)

    try:
        process = await asyncio.create_subprocess_shell(
            "shortlang tmp.sl",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            limit=4096  # Set a reasonable limit for the output
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5)

        if process.returncode is None:
            process.terminate()
            raise asyncio.TimeoutError("Process timed out.")

        # response = f"**Output:**\n```\n{stdout.decode()[:1500]}\n```\n**Error:**\n```\n{stderr.decode()}\n```"

        embed = discord.Embed()

        stdout = stdout.decode()

        if len(stdout) != 0:
            output = f"```\n{stdout.decode()[:1500]}\n```"
        else:
            output = "*No output.*"

        embed.add_field(name="Program Output", value=output, inline=False)

        stderr = stderr.decode()
        embed.color = discord.colour.parse_hex_number("8080FF")

        if len(stderr) != 0:
            embed.add_field(name="Compiler output", value=f"```\n{stderr[:500]}\n```", inline=False)
            embed.color = discord.colour.parse_hex_number("FF0000")


        await ctx.reply(embed=embed)

    except asyncio.TimeoutError:
        await ctx.reply("The process timed out.")



bot.run(os.getenv("TOKEN"))
