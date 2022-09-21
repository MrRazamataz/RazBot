# MrRazamataz's RazBot
# reaction roles cog
import aiohttp
import discord
from discord.ext import commands
from cogs.management.database import check_role_permission, add_reaction_role
import emoji



class reactionRoles(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.hybrid_group(name="reactionroles", aliases=["rr"])
    async def reactionroles(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @reactionroles.command(name="create")
    async def create(self, ctx: commands.Context, message_id: discord.Message, emoji: str, role: discord.Role) -> None:
        """
        Create a reaction role.
        """
        emojis = emoji.unicode_codes.EMOJI_UNICODE["en"].values()
        print(str(emoji.encode("utf-8")))
        await ctx.defer(ephemeral=True)
        if await check_role_permission(ctx.author, "manage_server"):
            await add_reaction_role(message_id.id, emoji, role.id)
            await message_id.add_reaction(emoji)
            await ctx.send("Reaction role created!")

        else:
            await ctx.send(
                f"Sorry, {ctx.author.name}, you don't have permission for that. Required permission: `manage server settings`.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(reactionRoles(bot))
