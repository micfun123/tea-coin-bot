import discord
from discord.ext import commands
from discord.ui import View, Button
import aiosqlite
from io import BytesIO
import time


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.slash_command()
    async def makefile(self, ctx):
        async with aiosqlite.connect("economy.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS economy (user_id INTEGER, money INTEGER)")
            await db.commit()
            #add the bank to the file
            await db.execute("INSERT OR IGNORE INTO economy (user_id, money) VALUES (?, ?)", ("Bank", 100000000))
            await db.commit()
            await ctx.respond("File made")


    @commands.slash_command()
    async def balance(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        async with aiosqlite.connect("economy.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS economy (user_id INTEGER, money INTEGER)")
            await db.commit()
            data = await db.execute("SELECT money FROM economy WHERE user_id = ?", (user.id,))
            data = await data.fetchone()
            if data is None:
                await db.execute("INSERT OR IGNORE INTO economy (user_id, money) VALUES (?, ?)", (user.id, 0))
                await db.commit()
                await ctx.respond(f"{user.mention} has 0 coins")
            else:
                await ctx.respond(f"{user.mention} has {data[0]} coins")


    @commands.slash_command()
    async def send(self,ctx,user: discord.Member = None, amount: int = None):
        if user is None:
            await ctx.respond("You need to specify a user")
        elif amount is None:
            await ctx.respond("You need to specify an amount")
        else:
            async with aiosqlite.connect("economy.db") as db:
                user1 = await db.execute("SELECT money FROM economy WHERE user_id = ?", (ctx.author.id,))
                user1 = await user1.fetchone()
                user2 = await db.execute("SELECT money FROM economy WHERE user_id = ?", (user.id,))
                user2 = await user2.fetchone()
                if user1[0] < amount:
                    await ctx.respond("You don't have enough money")
                else:
                    await db.execute("UPDATE economy SET money = ? WHERE user_id = ?", (user1[0] - amount, ctx.author.id))
                    await db.commit()
                    await db.execute("UPDATE economy SET money = ? WHERE user_id = ?", (user2[0] + amount, user.id))
                    await db.commit()
                    await ctx.respond(f"You sent {user.mention} {amount} coins")
                    await user.send(f"{ctx.author.mention} sent you {amount} coins")
                
    @commands.slash_command()
    @commands.is_owner()
    async def bank_control(self, ctx, user: discord.Member = None, amount: int = None):
        if user is None:
            await ctx.respond("You need to specify a user")
        elif amount is None:
            await ctx.respond("You need to specify an amount")
        else:
             async with aiosqlite.connect("economy.db") as db:
                bank = await db.execute("SELECT money FROM economy WHERE user_id = ?", ("Bank",))
                bank = await bank.fetchone()
                bankmoney = bank[0]
                if bankmoney < amount:
                    await ctx.respond("The bank doesn't have enough money")
                else:
                    await db.execute("UPDATE economy SET money = ? WHERE user_id = ?", (bankmoney - amount, "Bank"))
                    await db.commit()
                    money = await db.execute("SELECT money FROM economy WHERE user_id = ?", (user.id,))
                    money = await money.fetchone()
                    await db.execute("UPDATE economy SET money = ? WHERE user_id = ?", (money[0] + amount, user.id))
                    await db.commit()
                    await ctx.respond(f"You gave {user.mention} {amount} coins")
                    
    @commands.slash_command()
    async def baltop(self, ctx):
        async with aiosqlite.connect("economy.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS economy (user_id INTEGER, money INTEGER)")
            await db.commit()
            data = await db.execute("SELECT user_id, money FROM economy ORDER BY money DESC LIMIT 10")
            data = await data.fetchall()
            embed = discord.Embed(title="Top 10 richest people", color=discord.Color.blurple())
            for i in range(len(data)):
                embed.add_field(name=f"{i + 1}. {self.client.get_user(data[i][0])}", value=f"{data[i][1]} coins", inline=False)
            await ctx.respond(embed=embed)





def setup(client):
    client.add_cog(Economy(client))