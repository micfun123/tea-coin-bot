import discord
from discord.ext import commands
from discord.ui import View, Button
import aiosqlite
from io import BytesIO
import time
import random


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.slash_command()
    async def makefile(self, ctx):
        async with aiosqlite.connect("economy.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS economy (user_id Float, money Float,daily INTEGER)")
            await db.commit()
            await db.execute("CREATE TABLE IF NOT EXISTS inventory (user_id Float, item TEXT)")
            await db.commit()
            await db.execute("CREATE TABLE IF NOT EXISTS shop (item TEXT, price INTEGER)")
            await db.commit()



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
                await db.execute("INSERT OR IGNORE INTO economy (user_id, money) VALUES (?, ?)", (user.id, 0,0))
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
                try:
                    user1 = await db.execute("SELECT money FROM economy WHERE user_id = ?", (ctx.author.id,))
                    user1 = await user1.fetchone()
                    user2 = await db.execute("SELECT money FROM economy WHERE user_id = ?", (user.id,))
                    user2 = await user2.fetchone()
                    if user1[0] < amount:
                        await ctx.respond("You don't have enough money")
                    else:
                        await db.execute("UPDATE economy SET money = ? WHERE user_id = ?", (user2[0] + amount, user.id))
                        await db.commit()
                        await db.execute("UPDATE economy SET money = ? WHERE user_id = ?", (user1[0] - amount, ctx.author.id))
                        await db.commit()
                    
                        await ctx.respond(f"You sent {user.mention} {amount} coins")
                        await user.send(f"{ctx.author.mention} sent you {amount} coins")
                except Exception as e:
                    await ctx.respond(f"User has not made a bank account yet.")
                
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
                try:
                    embed.add_field(name=f"{i + 1}. {self.client.get_user(data[i][0]).name}", value=f"{data[i][1]} coins", inline=False)
                except:
                    embed.add_field(name=f"{i + 1}. <@{data[i][0]}>", value=f"{data[i][1]} coins", inline=False)
            await ctx.respond(embed=embed)

    @commands.slash_command()
    async def daily(self, ctx):
        async with aiosqlite.connect("economy.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS economy (user_id INTEGER, money INTEGER, daily INTEGER)")
            await db.commit()
            data = await db.execute("SELECT * FROM economy WHERE user_id = ?", (ctx.author.id,))
            data = await data.fetchone()
            if data is None:
                await db.execute("INSERT OR IGNORE INTO economy (user_id, money, daily) VALUES (?, ?, ?)", (ctx.author.id, 5, time.time()))
                await db.commit()
                await ctx.respond("You have claimed your daily reward")
            else:
                if time.time() - data[2] >= 86400:
                    await db.execute("UPDATE economy SET money = ? WHERE user_id = ?", (data[1] + 5, ctx.author.id))
                    await db.commit()
                    await db.execute("UPDATE economy SET daily = ? WHERE user_id = ?", (time.time(), ctx.author.id))
                    await db.commit()
                    await ctx.respond("You have claimed your daily reward")
                else:
                    await ctx.respond(f"You have to wait {int(86400 - (time.time() - data[2]))/3600} hours to claim your daily reward")
                        
    @commands.slash_command(name="rps")
    async def rps(self, ctx, rps: str,amount:int):
        choices = ["rock", "paper", "scissors"]
        cpu_choice = random.choice(choices)
        em = discord.Embed(title="Rock Paper Scissors")
        rps = rps.lower()

        async with aiosqlite.connect("economy.db") as db:
            data = await db.execute("SELECT * FROM economy WHERE user_id = ?", (ctx.author.id,))
            data = await data.fetchone()
            if data[0] < amount:
                await("You do not have enough money to bet")
                await db.execute("UPDATE economy SET money = ? WHERE user_id = ?", (data[1] - amount, ctx.author.id))
                await db.commit()
            else:
                if rps == 'rock':
                    if cpu_choice == 'rock':
                        outcome = "It's a tie!"
                    elif cpu_choice == 'scissors':
                        outcome = "You win!"
                    elif cpu_choice == 'paper':
                        outcome = "You lose!"

                elif rps == 'paper':
                    if cpu_choice == 'paper':
                        outcome = "It's a tie!"
                    elif cpu_choice == 'rock':
                        outcome = "You win!"
                    elif cpu_choice == 'scissors':
                        outcome = "You lose!"

                elif rps == 'scissors':
                    if cpu_choice == 'scissors':
                        outcome = "It's a tie!"
                    elif cpu_choice == 'paper':
                        outcome = "You win!"
                    elif cpu_choice == 'rock':
                        outcome = "You lose!"

                else:
                    outcome = "Invalid Input"

                if outcome == "You win!":
                    await db.execute("UPDATE economy SET money = ? WHERE user_id = ?", (data[1] + amount + amount*0.05, ctx.author.id))
                    await db.commit()
                    em.description = outcome
                    em.add_field(name="Your Choice", value=rps)
                    em.add_field(name="Bot Choice", value=cpu_choice)
                    em.add_field(name="Profit",value=amount*0.05)
                    await ctx.respond(embed=em)

                if outcome == "It's a tie!":
                   em.description = outcome
                   em.add_field(name="Your Choice", value=rps)
                   em.add_field(name="Bot Choice", value=cpu_choice)
                   em.add_field(name="Profit",value=0)
                   await ctx.respond(embed=em)

                if outcome == "It's a tie!":
                   em.description = outcome
                   em.add_field(name="Your Choice", value=rps)
                   em.add_field(name="Bot Choice", value=cpu_choice)
                   em.add_field(name="Profit",value=-amount)
                   await ctx.respond(embed=em)





    @commands.slash_command()
    @commands.is_owner()
    async def restarttimer(self, ctx):
        async with aiosqlite.connect("economy.db") as db:
            await db.execute("UPDATE economy SET daily = ? WHERE user_id = ?", (0, ctx.author.id))
            await db.commit()
            await ctx.respond("Timer has been reset")




def setup(client):
    client.add_cog(Economy(client))