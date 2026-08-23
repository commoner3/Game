import discord
from discord.ext import commands

class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='hello')
    async def hello(self, ctx):
        """Say hello to the user"""
        await ctx.send(f'Hello {ctx.author.name}! 👋')
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! 🏓 ({latency}ms)')

async def setup(bot):
    await bot.add_cog(Hello(bot))
