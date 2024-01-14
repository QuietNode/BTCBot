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
            bitcoin_fun_facts = self.fact_bank.read_facts()
            random.shuffle(bitcoin_fun_facts)
            for fact in bitcoin_fun_facts:
                yield fact

    @commands.group(invoke_without_command=True)
    async def ff(self, ctx):
        id, fact, author, date = next(self.fact_generator)
        embed = discord.Embed(title=f"Fun Fact #{id} authored at {date} by {author}", description=fact, color=0x00ff00)
        await ctx.send(embed=embed)

    @ff.command(name="help")
    async def ff_help(self, ctx):
        embed = discord.Embed(title=f"Fun Fact Help", description="Fun Fact Commands", color=0x00ff00)
        embed.add_field(name="!ff", value="Get a random fact", inline=False)
        embed.add_field(name="!ff read <id>", value="Get a fact by id", inline=False)
        embed.add_field(name="!ff total", value="Get the total number of facts", inline=False)
        embed.add_field(name="!ff create <fact>", value="Create a new fact", inline=False)
        embed.add_field(name="!ff update <id> <fact>", value="Update a fact", inline=False)
        embed.add_field(name="!ff delete <id>", value="Delete a fact", inline=False)
        message = await ctx.send(embed=embed)

        await asyncio.sleep(60)
        await message.delete()

    @ff.command(name="read")
    async def ff_read(self, ctx, *args):
        if len(args) == 0:
            await ctx.send("To use fact use the format: `!ff get <id>`")
        try:
            id = int(args[0])
            if id < 0:
                return await ctx.send("id must be a positive integer")
        except ValueError as _:
            return await ctx.send("Non-integer id")
        fact_by_id = self.fact_bank.read_fact(id)
        if fact_by_id is None:
            return await ctx.send("Fact not found")
        id, fact, author, date = fact_by_id
        embed = discord.Embed(title=f"Fun Fact #{id} authored at {date} by {author}", description=fact, color=0x00ff00)
        await ctx.send(embed=embed)

    @ff.command(name="total")
    async def ff_total(self, ctx):
        await ctx.send("There are " + str(self.fact_bank.total_facts()) + " facts in the database.")

    @ff.command(name="create")
    async def ff_create(self, ctx):
        author = ctx.message.author.name
        fact = " ".join(ctx.message.content.split(" ")[2:])

        await self.wait_for_reaction(ctx, fact, 0, f"Request to add fact.")
        self.fact_bank.create_fact(fact, author, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        await ctx.send("Fact added by " + author)

    @ff.command(name="update")
    async def ff_update(self, ctx, *args):
        if len(args) < 2:
            return await ctx.send("To use update use the format: `!ff update <id> <new fact>`")
        try:
            id = int(args[0])
            if id < 0:
                return await ctx.send("id must be a positive integer")
        except ValueError as _:
            return await ctx.send("Non-integer id")
        if not args:
            return await ctx.send("To use update use the format: `!ff update <id> <new fact>`")

        fact = " ".join(ctx.message.content.split(" ")[3:])
        await self.wait_for_reaction(ctx, fact, id, f"Request to update fact with id {id}.")

        self.fact_bank.update_fact(id, fact)
        await ctx.send(f"Entry updated.")

    @ff.command(name="delete")
    async def ff_delete(self, ctx, *args):
        if len(args) != 1:
            return await ctx.send("To use delete use the format: `!ff delete <id>`")
        try:
            id = int(args[0])
            if id < 0:
                return await ctx.send("id must be a positive integer")
        except ValueError as _:
            return await ctx.send("Non-integer id")
        if not args:
            return await ctx.send("To use delete use the format: `!ff delete <id>`")

        await self.wait_for_reaction(ctx, "", id, f"Request to delete fact with id {id}.")

        self.fact_bank.delete_fact(id)
        await ctx.send(f"Entry deleted.")

    async def wait_for_reaction(self, ctx, fact, id, description):
        embed = discord.Embed(title=description, description=fact, color=0x00ff00)
        message = await ctx.send(embed=embed)

        reaction_emoji = '👍'
        await message.add_reaction(reaction_emoji)
        check = await self.reaction_check(ctx, message, reaction_emoji)
        try:
            reactions_count = 0
            while reactions_count < 3:
                reaction, user = await self.bot.wait_for('reaction_add', check=check)
                reactions_count = reaction.count

        except Exception as _:
            await ctx.send(f"An error occurred. Please try again.")
            return

        await message.delete()

    async def reaction_check(self, ctx, message, reaction_emoji):
        def check(reaction, user):
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
