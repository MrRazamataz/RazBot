# MrRazamataz's RazBot
# database man cog
import yaml
from discord.ext import commands
import aiofiles
import aiomysql
import datetime


# gen now time func

def get_now_time():
    return datetime.datetime.utcnow()


# apod
async def apod_on(guild_id, channel_id):
    pool = await aiomysql.create_pool(host=tokens["database_info"]["host"], port=3306,
                                      user=tokens["database_info"]["username"],
                                      password=tokens["database_info"]["password"],
                                      db='razbotxy_botDB')
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE guild_settings SET apod_channel = {channel_id} WHERE id = {guild_id}")
            await conn.commit()
            conn.close()
            pool.close()
            await pool.wait_closed()


async def apod_off(guild_id):
    pool = await aiomysql.create_pool(host=tokens["database_info"]["host"], port=3306,
                                      user=tokens["database_info"]["username"],
                                      password=tokens["database_info"]["password"],
                                      db='razbotxy_botDB')
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE guild_settings SET apod_channel = NULL WHERE id = {guild_id}")
            await conn.commit()
            conn.close()
            pool.close()
            await pool.wait_closed()


async def apod_run():
    pool = await aiomysql.create_pool(host=tokens["database_info"]["host"], port=3306,
                                      user=tokens["database_info"]["username"],
                                      password=tokens["database_info"]["password"],
                                      db='razbotxy_botDB')
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            cursor = await cur.execute(f"SELECT apod_channel FROM guild_settings")
            output = await cursor.fetchall()
            conn.close()
            pool.close()
            await pool.wait_closed()
            return output


# mod
async def add_ban(member_id, guild_id, moderator_id, reason):
    pool = await aiomysql.create_pool(host=tokens["database_info"]["host"], port=3306,
                                      user=tokens["database_info"]["username"],
                                      password=tokens["database_info"]["password"],
                                      db='razbotxy_botDB')
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO log_bans (member_id, guild_id, moderator_id, datetime, reason, revoked) VALUES (%s, %s, %s, %s, %s, %s)",
                (member_id, guild_id, moderator_id, get_now_time(), reason, 0)
            )
            await conn.commit()
            conn.close()
            pool.close()
            await pool.wait_closed()


async def add_unban(member_id, guild_id, moderator_id, reason):
    pool = await aiomysql.create_pool(host=tokens["database_info"]["host"], port=3306,
                                      user=tokens["database_info"]["username"],
                                      password=tokens["database_info"]["password"],
                                      db='razbotxy_botDB')
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO log_unbans (member_id, guild_id, moderator_id, datetime, reason) VALUES (%s, %s, %s, %s, %s)",
                (member_id, guild_id, moderator_id, get_now_time(), reason)
            )
            await conn.commit()
            conn.close()
            pool.close()
            await pool.wait_closed()
            return


async def revoke_ban(member_id, guild_id):
    print("working...")
    pool = await aiomysql.create_pool(host=tokens["database_info"]["host"], port=3306,
                                      user=tokens["database_info"]["username"],
                                      password=tokens["database_info"]["password"],
                                      db='razbotxy_botDB')
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE log_bans SET revoked = 1 WHERE guild_id = {guild_id} AND member_id = {member_id}")
            await conn.commit()
            print("worked.")
            conn.close()
            pool.close()
            await pool.wait_closed()
            return


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
        pool = await aiomysql.create_pool(host=tokens["database_info"]["host"], port=3306,
                                          user=tokens["database_info"]["username"],
                                          password=tokens["database_info"]["password"],
                                          db='razbotxy_botDB')
        print("[DB] Connecting to DB...")
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # await cur.execute(create_table_query)
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
                await cur.execute(
                    'CREATE TABLE IF NOT EXISTS log_bans (member_id BIGINT, guild_id BIGINT, moderator_id BIGINT, datetime DATETIME, reason TEXT, revoked INT)')
                await cur.execute(
                    'CREATE TABLE IF NOT EXISTS log_unbans (member_id BIGINT, guild_id BIGINT, moderator_id BIGINT, datetime DATETIME, reason TEXT)')
                await conn.commit()

        conn.close()
        pool.close()
        await pool.wait_closed()
        print("[DB] Connection closed.")


async def setup(bot):
    await bot.add_cog(db(bot))
