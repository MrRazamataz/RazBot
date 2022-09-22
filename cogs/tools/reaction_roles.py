# MrRazamataz's RazBot
# reaction roles cog
import aiohttp
import discord
from discord.ext import commands
from cogs.management.database import check_role_permission, add_reaction_role, get_reaction_role
import emoji


class reactionRoles(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.hybrid_group(name="reactionroles", aliases=["rr"])
    async def reactionroles(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @reactionroles.command(name="create")
    async def create(self, ctx: commands.Context, message_id: discord.Message, emoji_input: str,
                     role: discord.Role) -> None:
        """
        Create a reaction role.
        """
        emoji_input = emoji.demojize(emoji_input)
        await ctx.defer(ephemeral=True)
        if await check_role_permission(ctx.author, "manage_server"):
            await add_reaction_role(message_id.id, emoji_input, role.id)
            await message_id.add_reaction(emoji.emojize(emoji_input))
            await ctx.send("Reaction role created!", ephemeral=True)

        else:
            await ctx.send(
                f"Sorry, {ctx.author.name}, you don't have permission for that. Required permission: `manage server settings`.",
                ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.member.bot:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if payload.emoji.is_custom_emoji():
            emoji_input = f"<:{payload.emoji.name}:{payload.emoji.id}>"
        else:
            emoji_input = emoji.demojize(payload.emoji.name)
        roles = await get_reaction_role(payload.message_id, emoji_input)
        for role in roles:  # support multiple roles on one reaction
            role = guild.get_role(role[0])
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.member.bot:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if payload.emoji.is_custom_emoji():
            emoji_input = f"<:{payload.emoji.name}:{payload.emoji.id}>"
        else:
            emoji_input = emoji.demojize(payload.emoji.name)
        roles = await get_reaction_role(payload.message_id, emoji_input)
        for role in roles:  # support multiple roles on one reaction
            role = guild.get_role(role[0])
            await member.remove_roles(role)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(reactionRoles(bot))
