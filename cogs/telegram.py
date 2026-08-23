import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import aiohttp

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

class Telegram(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.telegram_links = {}  # Store user telegram links {discord_id: telegram_username}
        self.telegram_api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    
    @commands.group(name='telegram')
    async def telegram(self, ctx):
        """Telegram integration commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `!telegram link`, `!telegram unlink`, `!telegram status`, or `!telegram send`")
    
    @telegram.command(name='link')
    async def link(self, ctx, username: str):
        """Link your Discord account to Telegram"""
        self.telegram_links[ctx.author.id] = username
        await ctx.send(f"✅ Successfully linked to Telegram user: `{username}`")
        
        # Send notification to Telegram
        message = f"Discord user {ctx.author.name} has linked their account!"
        await self._send_telegram_message(message)
    
    @telegram.command(name='unlink')
    async def unlink(self, ctx):
        """Unlink your Telegram account"""
        if ctx.author.id in self.telegram_links:
            username = self.telegram_links[ctx.author.id]
            del self.telegram_links[ctx.author.id]
            await ctx.send(f"✅ Successfully unlinked from Telegram")
            
            message = f"Discord user {ctx.author.name} has unlinked their Telegram account."
            await self._send_telegram_message(message)
        else:
            await ctx.send("❌ You don't have a Telegram account linked!")
    
    @telegram.command(name='status')
    async def status(self, ctx):
        """Check Telegram link status"""
        if ctx.author.id in self.telegram_links:
            username = self.telegram_links[ctx.author.id]
            await ctx.send(f"✅ Linked to Telegram: `{username}`")
        else:
            await ctx.send("❌ No Telegram account linked. Use `!telegram link <username>`")
    
    @telegram.command(name='send')
    async def send(self, ctx, *, message: str):
        """Send a message to linked Telegram account"""
        if ctx.author.id not in self.telegram_links:
            await ctx.send("❌ You must link a Telegram account first! Use `!telegram link <username>`")
            return
        
        telegram_user = self.telegram_links[ctx.author.id]
        full_message = f"From Discord ({ctx.author.name}): {message}"
        
        success = await self._send_telegram_message(full_message)
        if success:
            await ctx.send(f"✅ Message sent to Telegram!")
        else:
            await ctx.send(f"❌ Failed to send message to Telegram")
    
    async def _send_telegram_message(self, message: str):
        """Send message to Telegram"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.telegram_api}/sendMessage"
                payload = {
                    'chat_id': TELEGRAM_CHAT_ID,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                async with session.post(url, json=payload) as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

async def setup(bot):
    await bot.add_cog(Telegram(bot))
