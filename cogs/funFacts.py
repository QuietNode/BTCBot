import asyncio
import datetime
import random

import discord
from discord.ext import commands

from db import Database


class FunFacts(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.fact_generator = self.get_fact()
        self.fact_bank = Database()

    def get_fact(self):
        while True:
            bitcoin_fun_facts = self.fact_bank.get_facts()
            random.shuffle(bitcoin_fun_facts)
            for fact in bitcoin_fun_facts:
                yield fact

    @commands.group(invoke_without_command=True)
    async def ff(self, ctx):
        id, fact, author, date = next(self.fact_generator)
        embed = discord.Embed(title=f"Fun Fact #{id} authored at {date} by {author}", description=fact, color=0x00ff00)
        await ctx.send(embed=embed)

    @ff.command(name="get")
    async def fact(self, ctx, *args):
        if len(args) == 0:
            await ctx.send("To use fact use the format: `!fact <id>`")
        try:
            id = int(args[0])
            if id < 0:
                return await ctx.send("id must be a positive integer")
        except ValueError as _:
            return await ctx.send("Non-integer id")
        fact_by_id = self.fact_bank.get_fact(id)
        id, fact, author, date = fact_by_id
        embed = discord.Embed(title=f"Fun Fact #{id} authored at {date} by {author}", description=fact, color=0x00ff00)
        await ctx.send(embed=embed)

    @ff.command(name="total")
    async def ff_total(self, ctx):
        await ctx.send("There are " + str(self.fact_bank.total_facts()) + " facts in the database.")

    @ff.command(name="add")
    async def ff_add(self, ctx):
        author = ctx.message.author.name
        fact = str(ctx.message.content[9:])

        embed = discord.Embed(title="Two approved users required for approval.", description=fact, color=0x00ff00)
        message = await ctx.send(embed=embed)

        reaction_emoji = '👍'
        await message.add_reaction(reaction_emoji)
        check = self.reaction_check(ctx, message, reaction_emoji)
        try:
            reactions_count = 0
            while reactions_count < 3:
                reaction, user = await self.bot.wait_for('reaction_add', check=check)
                reactions_count = reaction.count

        except:
            pass
        self.fact_bank.add_fact(fact, author, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        await ctx.send("Fact added by " + author)
        await message.delete()

    def reaction_check(self, ctx, message, reaction_emoji):
        async def check(reaction, user):
            if reaction.message.id != message.id:
                return False
            if user == self.bot.user:
                return False

            if str(reaction.emoji) != reaction_emoji:
                return False

            mod_role = discord.utils.get(ctx.guild.roles, name="mod")
            if mod_role in user.roles:
                reaction.count = reaction.count + 2
                return True
            approved_role = discord.utils.get(ctx.guild.roles, name="Approved User")

            if approved_role in user.roles:
                return True
            else:
                asyncio.create_task(reaction.remove(user))
                return False
        return check


async def setup(bot):
    await bot.add_cog(FunFacts(bot))
