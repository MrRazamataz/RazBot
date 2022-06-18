# MrRazamataz's RazBot
# database man cog
import asyncio

import yaml
from discord.ext import commands
import aiofiles
import aiomysql
import datetime


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
            conn.close()


async def apod_off(guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE guild_settings SET apod_channel = NULL WHERE id = {guild_id}")
            await conn.commit()
            conn.close()


async def apod_run():
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            cursor = await cur.execute(f"SELECT apod_channel FROM guild_settings")
            output = await cursor.fetchall()
            conn.close()
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
            conn.close()


async def add_unban(member_id, guild_id, moderator_id, reason):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO log_unbans (member_id, guild_id, moderator_id, datetime, reason) VALUES (%s, %s, %s, %s, %s)",
                (member_id, guild_id, moderator_id, get_now_time(), reason)
            )
            await conn.commit()
            conn.close()
            return


async def revoke_ban(member_id, guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"UPDATE log_bans SET revoked = 1 WHERE guild_id = {guild_id} AND member_id = {member_id}")
            await conn.commit()
            conn.close()
            return


async def add_kick(member_id, guild_id, moderator_id, reason):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO log_kicks (member_id, guild_id, moderator_id, datetime, reason) VALUES (%s, %s, %s, %s, %s)",
                (member_id, guild_id, moderator_id, get_now_time(), reason)
            )
            await conn.commit()
            conn.close()


async def add_warn(member_id, guild_id, moderator_id, reason):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO warns (member_id, guild_id, moderator_id, datetime, reason) VALUES (%s, %s, %s, %s, %s)",
                (member_id, guild_id, moderator_id, get_now_time(), reason)
            )
            await conn.commit()
            conn.close()


async def get_user_guild_warncount(member_id, guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            count = await cur.execute(
                f"SELECT id FROM warns WHERE member_id = {member_id} AND guild_id = {guild_id}")
            count = await cur.fetchall()
            count = len(count)
            conn.close()
            return count


async def get_all_warnings_user_guild(member_id, guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"SELECT * FROM warns WHERE member_id = {member_id} AND guild_id = {guild_id}")
            output = await cur.fetchall()
            conn.close()
            return output


async def mod_log(moderator_id, guild_id, action):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"INSERT INTO mod_log (moderator_id, guild_id, action, datetime) VALUES (%s, %s, %s, %s)",
                (moderator_id, guild_id, action, get_now_time())
            )
            await conn.commit()
            conn.close()


async def delete_warning(warn_id, guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT * FROM warns WHERE id = {warn_id} AND guild_id = {guild_id}")
            query = await cur.fetchall()
            if len(query) == 0:
                conn.close()
                return False
            else:
                await cur.execute(f"DELETE FROM warns WHERE id = {warn_id} AND guild_id = {guild_id}")
                await conn.commit()
                conn.close()
                return True


async def clear_all_users_warnings(member_id, guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"DELETE FROM warns WHERE member_id = {member_id} AND guild_id = {guild_id}")
            await conn.commit()
            conn.close()
            return


async def clear_all_guild_warnings(guild_id):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"DELETE FROM warns WHERE guild_id = {guild_id}")
            await conn.commit()
            conn.close()
            return


# permissions
async def set_role_permission(role_id, permission, state):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"INSERT INTO permissions (role_id, permission, state) VALUES (%s, %s, %s)",
                (role_id, permission, state)
            )
            await conn.commit()
            conn.close()
            return

async def check_role_permission(role_id, permission):
    async with cog_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"SELECT state FROM permissions WHERE role_id = {role_id} AND permission = '{permission}'"
            )
            output = await cur.fetchall()
            conn.close()
            return output

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
                    'CREATE TABLE IF NOT EXISTS guild_settings (id BIGINT, member_count INT, apod_channel BIGINT)')
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
                await conn.commit()
                print("[DB] Tables present or created.")
        conn.close()
        print("[DB] Connection cursor closed.")


async def setup(bot):
    await database_setup()
    await bot.add_cog(db(bot))
