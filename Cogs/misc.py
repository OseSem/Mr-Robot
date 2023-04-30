from ast import Delete
from typing import Union

import disnake
from disnake.ext import commands

from utils import DeleteButton, Embeds


class EmbedModal(disnake.ui.Modal):
    def __init__(self, color):
        self.color = color
        components = [
            disnake.ui.TextInput(
                label="Image url",
                placeholder="Enter image here",
                custom_id="image",
                style=disnake.TextInputStyle.short,
                required=False,
            ),
            disnake.ui.TextInput(
                label="Title",
                placeholder="Enter title here",
                custom_id="title",
                style=disnake.TextInputStyle.short,
            ),
            disnake.ui.TextInput(
                label="Body",
                placeholder="Enter content here",
                custom_id="body",
                style=disnake.TextInputStyle.paragraph,
            ),
        ]
        super().__init__(
            title="Embed Generator", custom_id="embed_generator", components=components
        )

    async def callback(self, interaction: disnake.ModalInteraction):
        title = interaction.text_values["title"]
        content = interaction.text_values["body"]
        image = interaction.text_values["image"]

        embed = Embeds.emb(self.color, title, content)
        embed.set_image(image)
        embed.set_footer(text=interaction.guild.name)
        await interaction.send(
            embed=embed, view=DeleteButton(author=interaction.author)
        )

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction):
        await inter.response.send_message(
            embed=Embeds.emb(Embeds.red, "Oops! Something went wrong :cry:"),
            ephemeral=True,
        )


class Misc(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.slash_command(name="embed", dm_permission=False)
    async def slash_embed(
        self,
        interaction: disnake.CommandInteraction,
        color: disnake.Color = disnake.Color.random(),
    ):
        """
        Creates embed

        Parameters
        ----------
        color: Hex code or name of colour
        """
        await interaction.response.send_modal(modal=EmbedModal(color=color))

    @commands.slash_command(name="userinfo", dm_permission=False)
    async def slash_userinfo(
        self, interaction, member: Union[disnake.Member, None] = None
    ):
        """
        Shows user info

        Parameters
        ----------
        member : Member to show info
        """
        if member is None:
            member = interaction.author
        embed = Embeds.emb(member.color, f"{member} Information")
        try:
            embed.set_thumbnail(url=member.display_avatar.url)
        except Exception:
            embed.set_thumbnail(
                url="https://cdn.logojoy.com/wp-content/uploads/"
                "20210422095037/discord-mascot.png"
            )
        embed.add_field(name="Name", value=member.name, inline=False)
        embed.add_field(name="Nickname", value=member.nick, inline=False)
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(
            name="Account Created",
            value=member.created_at.strftime("%a %#d %B %Y, %I:%M %p UTC"),
            inline=False,
        )
        embed.add_field(
            name="Joined",
            value=member.joined_at.strftime("%a %#d %B %Y, %I:%M %p UTC"),
            inline=False,
        )
        members = sorted(interaction.guild.members, key=lambda m: m.joined_at)
        embed.add_field(
            name="Join Position", value=str(members.index(member) + 1), inline=False
        )
        embed.add_field(name="Status", value=member.status, inline=False)
        embed.add_field(name="Activity: ", value=member.activity, inline=False)
        embed.add_field(
            name="Roles" if len(member.roles) > 1 else "Role",
            value=", ".join([role.mention for role in member.roles]),
            inline=False,
        )
        await interaction.send(
            embed=embed, view=DeleteButton(author=interaction.author)
        )


def setup(client: commands.Bot):
    client.add_cog(Misc(client))