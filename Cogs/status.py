import datetime
import os
import time

import disnake
import psutil
from disnake.ext import commands

from bot import PROXY, client, start_time
from utils import DeleteButton, Embeds, db


class Command_handling(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"\n [!] Logged in as {client.user}\n\n [!] Proxy: {PROXY}")
        os.system("echo '' > Servers.inf")
        present_guilds: list[str] = []
        for guild in self.bot.guilds:
            present_guilds.append(guild.id)
            with open("Servers.inf", "a+") as stats:
                stats.write(
                    f"""\n\n [+] {guild.name} --> {', '.join([ f'{channel.name} [{channel.id}]' for channel in guild.channels])} \n"""
                )
            data = {
                "$set": {
                    "guild_id": guild.id,
                    "guild_name": guild.name,
                }
            }
            db.config.update_one({"guild_id": guild.id}, data, upsert=True)
        for guild in db.config.find():
            if guild["guild_id"] not in present_guilds:
                db.config.delete_one({"guild_id": guild["guild_id"]})
                db.traffic.delete_one({"guild_id": guild["guild_id"]})
        with open("proxy_mode.conf", "r") as file:
            proxy_mode = file.read()
        if proxy_mode == "on":
            await self.bot.change_presence(
                status=disnake.Status.idle,
                activity=disnake.Game(name="In Starvation Mode"),
            )
        await self.bot.change_presence(
            activity=disnake.Streaming(
                name=f"In {len(client.guilds)} Servers",
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            )
        )

    @commands.slash_command(name="status", dm_permission=False)
    async def slash_status(self, interaction):
        """Shows status of the bot"""

        def get_greeter_status(feature):
            result = db.traffic.find_one({"guild_id": interaction.guild.id})
            if result is not None:
                try:
                    if len(str(result[feature])) > 0:
                        return ":white_check_mark:"
                    else:
                        raise KeyError()
                except KeyError:
                    return ":x:"

        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        embed = Embeds.emb(Embeds.green, "Status")
        embed.add_field(
            "Ping: ",
            f"{round(client.latency * 1000)}ms",
        )
        embed.add_field(
            "Uptime: ",
            f"{text}",
        )
        embed.add_field(
            "Cpu Usage: ",
            f"{psutil.cpu_percent()}%",
        )
        embed.add_field(
            "Memory Usage: ",
            f"{psutil.virtual_memory().percent}%",
        )
        embed.add_field(
            "Available Usage: ",
            f"{round(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)}%",
        )
        embed.add_field(
            "Users: ",
            interaction.guild.member_count,
        )
        embed.add_field(
            "Channels: ",
            len(interaction.guild.channels),
        )
        embed.add_field(
            "Welcomer: ",
            get_greeter_status("welcome_channel"),
        )
        embed.add_field(
            "Goodbyer: ",
            get_greeter_status("bye_channel"),
        )
        if interaction.author.id == self.bot.owner.id:
            embed.add_field(
                "Servers List",
                ":satellite: "
                + "\n:satellite: ".join(
                    [f"`{guild.name} {guild.id}`" for guild in self.bot.guilds]
                ),
                inline=False,
            )
        await interaction.send(
            embed=embed, view=DeleteButton(author=interaction.author)
        )


def setup(client: commands.Bot):
    client.add_cog(Command_handling(client))