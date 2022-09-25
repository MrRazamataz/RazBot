# MrRazamataz's RazBot
# database man cog
import asyncio

import yaml
from discord.ext import commands
import aiofiles
import aiomysql
import datetime
import os
import traceback


async def database_setup():
    with open("token.yml", mode="r") as file:
        tokens = yaml.safe_load(file)
    global cog_pool
    cog_pool = await aiomysql.create_pool(host=tokens["database_info"]["host"], port=3306,
                                          user=tokens["database_info"]["username"],
                                          password=tokens["database_info"]["password"],
                                          db='razbotxy_botDB')


# gen now time func

def get_now_time():
    return datetime.datetime.utcnow()


# apod
async def apod_on(guild_id, channel_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE guild_settings SET apod_channel = {channel_id} WHERE id = {guild_id}")
            await conn.commit()


async def apod_off(guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE guild_settings SET apod_channel = NULL WHERE id = {guild_id}")
            await conn.commit()


async def apod_run():
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            cursor = await cur.execute(f"SELECT apod_channel FROM guild_settings")
            output = await cursor.fetchall()
            return output


# mod
async def add_ban(member_id, guild_id, moderator_id, reason):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO log_bans (member_id, guild_id, moderator_id, datetime, reason, revoked) VALUES (%s, %s, %s, %s, %s, %s)",
                (member_id, guild_id, moderator_id, get_now_time(), reason, 0)
            )
            await conn.commit()


async def add_unban(member_id, guild_id, moderator_id, reason):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO log_unbans (member_id, guild_id, moderator_id, datetime, reason) VALUES (%s, %s, %s, %s, %s)",
                (member_id, guild_id, moderator_id, get_now_time(), reason)
            )
            await conn.commit()
            return


async def revoke_ban(member_id, guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"UPDATE log_bans SET revoked = 1 WHERE guild_id = {guild_id} AND member_id = {member_id}")
            await conn.commit()
            return


async def add_kick(member_id, guild_id, moderator_id, reason):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO log_kicks (member_id, guild_id, moderator_id, datetime, reason) VALUES (%s, %s, %s, %s, %s)",
                (member_id, guild_id, moderator_id, get_now_time(), reason)
            )
            await conn.commit()


async def add_warn(member_id, guild_id, moderator_id, reason):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO warns (member_id, guild_id, moderator_id, datetime, reason) VALUES (%s, %s, %s, %s, %s)",
                (member_id, guild_id, moderator_id, get_now_time(), reason)
            )
            await conn.commit()


async def get_user_guild_warncount(member_id, guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            count = await cur.execute(
                f"SELECT id FROM warns WHERE member_id = {member_id} AND guild_id = {guild_id}")
            count = await cur.fetchall()
            count = len(count)
            return count


async def get_all_warnings_user_guild(member_id, guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"SELECT * FROM warns WHERE member_id = {member_id} AND guild_id = {guild_id}")
            output = await cur.fetchall()
            return output


async def mod_log(moderator_id, guild_id, action):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"INSERT INTO mod_log (moderator_id, guild_id, action, datetime) VALUES (%s, %s, %s, %s)",
                (moderator_id, guild_id, action, get_now_time())
            )
            await conn.commit()


async def delete_warning(warn_id, guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT * FROM warns WHERE id = {warn_id} AND guild_id = {guild_id}")
            query = await cur.fetchall()
            if len(query) == 0:
                return False
            else:
                await cur.execute(f"DELETE FROM warns WHERE id = {warn_id} AND guild_id = {guild_id}")
                await conn.commit()
                return True


async def clear_all_users_warnings(member_id, guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"DELETE FROM warns WHERE member_id = {member_id} AND guild_id = {guild_id}")
            await conn.commit()
            return


async def clear_all_guild_warnings(guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"DELETE FROM warns WHERE guild_id = {guild_id}")
            await conn.commit()
            return


# reaction roles
async def add_reaction_role(msg_id, emoji, role_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"INSERT INTO reaction_roles (msg_id, emoji, role_id) VALUES (%s, %s, %s)",
                (msg_id, emoji, role_id)
            )
            await conn.commit()
            return


async def check_for_reaction_role_exists(msg_id, emoji, role_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"SELECT * FROM reaction_roles WHERE msg_id = {msg_id} AND emoji = '{emoji}' AND role_id = {role_id}")
            query = await cur.fetchall()
            if len(query) == 0:
                return False
            else:
                return True


async def get_reaction_role(msg_id, emoji):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"SELECT role_id FROM reaction_roles WHERE msg_id = {msg_id} AND emoji = '{emoji}'")
            output = await cur.fetchall()
            return output


async def delete_reaction_role(msg_id, emoji, role_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"DELETE FROM reaction_roles WHERE msg_id = {msg_id} AND emoji = '{emoji}' AND role_id = {role_id}")
            await conn.commit()
            return


async def view_reaction_roles(msg_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"SELECT * FROM reaction_roles WHERE msg_id = {msg_id}")
            output = await cur.fetchall()
            return output


# reminders

async def add_reminder(user_id, reminder, time, dm_or_channel, channel_id=None):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            if channel_id:
                await cur.execute(
                    f"INSERT INTO reminders (user_id, channel_id, reminder, time, type) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, channel_id, reminder, time, dm_or_channel)
                )
            else:
                await cur.execute(
                    f"INSERT INTO reminders (user_id, reminder, time, type) VALUES (%s, %s, %s, %s)",
                    (user_id, reminder, time, dm_or_channel)
                )
            await conn.commit()
            return


permission_cache = {}


# permissions
async def set_role_permission(role_id, permission, state):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT state FROM permissions WHERE role_id = %s AND permission = %s",
                              (role_id, permission))
            query = await cur.fetchall()
            if len(query) == 0:
                await cur.execute(
                    f"INSERT INTO permissions (role_id, permission, state) VALUES (%s, %s, %s)",
                    (role_id, permission, state)
                )
                await conn.commit()
            else:
                await cur.execute(
                    f"UPDATE permissions SET state = %s WHERE role_id = %s AND permission = %s",
                    (state, role_id, permission)
                )
                await conn.commit()
            permission_cache.pop(f"{role_id}-{permission}")  # remove from cache
            return


async def check_role_permission(user_object, permission):
    try:
        if user_object.guild_permissions.administrator:  # if admin on discord, grant all perms
            return True
        for role in user_object.roles:  # check cache for permission of the role before checking the database
            try:
                if permission_cache[f"{role.id}-{permission}"] == True:
                    return True
                elif permission_cache[f"{role.id}-{permission}"] == False:
                    return False
            except KeyError:
                pass
        async with cog_pool.acquire() as conn:
            async with conn.cursor() as cur:
                for role in user_object.roles:
                    await cur.execute(
                        f"SELECT state FROM permissions WHERE role_id = {role.id} AND permission = '{permission}'"
                    )
                    output = await cur.fetchone()
                    if output:
                        if output[0] == "true":
                            permission_cache[f"{role.id}-{permission}"] = True
                            conn.close()
                            return True
                        elif output[0] == "false":
                            permission_cache[f"{role.id}-{permission}"] = False
                            conn.close()
                            return False
                else:
                    conn.close()
                    return False

    except Exception as e:
        traceback.print_exc()
        print(e)
        return False


async def set_panel_user(user_id, guild_id, state):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT state FROM panel_users WHERE user_id = %s AND guild_id = %s",
                              (user_id, guild_id))
            query = await cur.fetchall()
            if len(query) == 0:
                await cur.execute(
                    f"INSERT INTO panel_users (user_id, guild_id, state) VALUES (%s, %s, %s)",
                    (user_id, guild_id, state)
                )
                await conn.commit()
            else:
                await cur.execute(
                    f"UPDATE panel_users SET state = %s WHERE user_id = %s AND guild_id = %s",
                    (state, user_id, guild_id)
                )
                await conn.commit()
            return


# settings

async def set_log_channel(guild_id, channel_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"UPDATE guild_settings SET log_channel = {channel_id} WHERE id = {guild_id}")
            await conn.commit()
            return


async def set_welcome_channel(guild_id, channel_id, state):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            if state == "true":
                await cur.execute(f"UPDATE guild_settings SET welcome_channel = {channel_id} WHERE id = {guild_id}")
            else:
                await cur.execute(f"UPDATE guild_settings SET welcome_channel = NULL WHERE id = {guild_id}")
            await conn.commit()


class db(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    '''
        @commands.Cog.listener()
        async def on_guild_join(self, guild):
            async with aiosqlite.connect("database.db") as db:
                await db.execute(f"INSERT INTO guild_settings (id, member_count) VALUES ({guild.id}, {guild.member_count})")
                await db.commit()
    '''

    @commands.Cog.listener()
    async def on_ready(self):
        global tokens
        with open("token.yml", mode="r") as file:
            tokens = yaml.safe_load(file)
        '''
        pool = await aiomysql.create_pool(host=tokens["database_info"]["host"], port=3306,
                                          user=tokens["database_info"]["username"],
                                          password=tokens["database_info"]["password"],
                                          db='razbotxy_botDB')
        '''
        print("[DB] Connecting to DB...")
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    'CREATE TABLE IF NOT EXISTS guild_settings (id BIGINT, member_count INT, apod_channel BIGINT, log_channel BIGINT)')
                for guild in self.bot.guilds:
                    print(f"[DB] [Guild settings] Checking for settings in `{guild.id}`...")
                    check = await cur.execute(f"SELECT member_count FROM guild_settings WHERE id = {guild.id}")
                    if check == 0:
                        try:
                            await cur.execute(
                                f"INSERT INTO guild_settings (id, member_count) VALUES ({guild.id}, {guild.member_count})")
                            await conn.commit()
                        except Exception as e:
                            print(f"Error with {guild.id}! \n{e}")
                            pass
                    else:
                        await cur.execute(
                            f"UPDATE guild_settings SET member_count = {guild.member_count} WHERE id = {guild.id}")
                        await conn.commit()
                # create the rest of the tables that the bot needs if they don't exist
                print("[DB] Creating tables...")
                await cur.execute(
                    'CREATE TABLE IF NOT EXISTS log_bans (member_id BIGINT, guild_id BIGINT, moderator_id BIGINT, datetime DATETIME, reason TEXT, revoked INT)')
                await cur.execute(
                    'CREATE TABLE IF NOT EXISTS log_unbans (member_id BIGINT, guild_id BIGINT, moderator_id BIGINT, datetime DATETIME, reason TEXT)')
                await cur.execute(
                    'CREATE TABLE IF NOT EXISTS log_kicks (member_id BIGINT, guild_id BIGINT, moderator_id BIGINT, datetime DATETIME, reason TEXT)')
                await cur.execute(
                    'CREATE TABLE IF NOT EXISTS warns (member_id BIGINT, guild_id BIGINT, moderator_id BIGINT, datetime DATETIME, reason TEXT, id INT NOT NULL AUTO_INCREMENT PRIMARY KEY)')
                await cur.execute(
                    'CREATE TABLE IF NOT EXISTS mod_log (moderator_id BIGINT, guild_id BIGINT, action TEXT, datetime DATETIME)')
                await cur.execute(
                    'CREATE TABLE IF NOT EXISTS permissions (role_id BIGINT, permission TEXT, state TEXT)')
                await cur.execute(
                    'CREATE TABLE IF NOT EXISTS reaction_roles (msg_id BIGINT, emoji TEXT, role_id BIGINT)')
                await cur.execute(
                    'CREATE TABLE IF NOT EXISTS reminders (user_id BIGINT, channel_id BIGINT, reminder TEXT, time DATETIME, type TEXT')
                await conn.commit()
                print("[DB] Tables present or created.")
        conn.close()
        print("[DB] Connection cursor closed.")


async def setup(bot):
    await database_setup()
    await bot.add_cog(db(bot))
