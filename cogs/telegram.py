import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

class Telegram(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.telegram_links = {}  # Store user telegram links {discord_id: {phone, username, verified, code, code_expiry}}
        self.telegram_api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
        self.pending_codes = {}  # Store pending verification codes
    
    @commands.group(name='telegram')
    async def telegram(self, ctx):
        """Telegram integration commands"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="📱 Telegram Integration Commands",
                description="Link your Discord account to Telegram",
                color=discord.Color.blue()
            )
            embed.add_field(name="!telegram link <phone_number>", value="Start linking your Telegram account", inline=False)
            embed.add_field(name="!telegram verify <code>", value="Verify your Telegram account with code", inline=False)
            embed.add_field(name="!telegram status", value="Check Telegram link status", inline=False)
            embed.add_field(name="!telegram unlink", value="Unlink your Telegram account", inline=False)
            embed.add_field(name="!telegram send <message>", value="Send message to linked Telegram", inline=False)
            await ctx.send(embed=embed)
    
    @telegram.command(name='link')
    async def link(self, ctx, phone_number: str):
        """Start linking Telegram account with phone number"""
        
        # Validate phone number format
        if not phone_number.startswith('+'):
            await ctx.send("❌ Phone number must start with '+' (e.g., +233542635388)")
            return
        
        # Check if user already has a pending or linked account
        if ctx.author.id in self.telegram_links:
            status = self.telegram_links[ctx.author.id]
            if status.get('verified'):
                await ctx.send("✅ You already have a verified Telegram account linked!")
                return
            else:
                await ctx.send("⏳ You already have a pending verification. Use `!telegram verify <code>` to complete it.")
                return
        
        # Generate a verification code
        import random
        verification_code = str(random.randint(100000, 999999))
        expiry = datetime.now() + timedelta(minutes=10)
        
        # Store pending verification
        self.telegram_links[ctx.author.id] = {
            'phone': phone_number,
            'username': None,
            'verified': False,
            'code': verification_code,
            'code_expiry': expiry
        }
        
        # Create verification embed
        embed = discord.Embed(
            title="📱 Telegram Verification Started",
            color=discord.Color.green()
        )
        embed.add_field(name="📞 Phone Number", value=f"`{phone_number}`", inline=False)
        embed.add_field(name="⏱️ Verification Code", value=f"```{verification_code}```", inline=False)
        embed.add_field(name="📋 Instructions", value=
            "1. Open Telegram\n"
            "2. Search for our bot: @YourBotUsername\n"
            "3. Send this verification code to the bot: `{}`\n"
            "4. Come back here and use `!telegram verify <code>` to confirm".format(verification_code),
            inline=False
        )
        embed.add_field(name="⏰ Code Expires", value=f"<t:{int(expiry.timestamp())}:R>", inline=False)
        embed.set_footer(text="Keep this code private!")
        
        await ctx.send(embed=embed)
        await ctx.send(f"✅ Verification code generated! You have 10 minutes to verify.")
        
        # Send notification to Telegram
        message = f"Discord user {ctx.author.name} ({ctx.author.id}) has started Telegram linking with phone: {phone_number}"
        await self._send_telegram_message(message)
    
    @telegram.command(name='verify')
    async def verify(self, ctx, code: str):
        """Verify Telegram account with code"""
        
        if ctx.author.id not in self.telegram_links:
            await ctx.send("❌ You haven't started the linking process! Use `!telegram link <phone_number>` first.")
            return
        
        pending = self.telegram_links[ctx.author.id]
        
        # Check if already verified
        if pending.get('verified'):
            await ctx.send("✅ Your Telegram account is already verified!")
            return
        
        # Check if code has expired
        if datetime.now() > pending.get('code_expiry', datetime.now()):
            del self.telegram_links[ctx.author.id]
            await ctx.send("❌ Verification code has expired! Use `!telegram link <phone_number>` to start again.")
            return
        
        # Verify code
        if code == pending.get('code'):
            self.telegram_links[ctx.author.id]['verified'] = True
            self.telegram_links[ctx.author.id]['code'] = None
            
            embed = discord.Embed(
                title="✅ Telegram Account Verified!",
                color=discord.Color.green()
            )
            embed.add_field(name="📱 Phone Number", value=f"`{pending['phone']}`", inline=False)
            embed.add_field(name="📝 Status", value="Verified ✓", inline=False)
            embed.add_field(name="💡 Next Steps", value=
                "You can now:\n"
                "• Use `!telegram send <message>` to send messages to Telegram\n"
                "• Use `!telegram status` to check your link\n"
                "• Use `!telegram unlink` to disconnect",
                inline=False
            )
            await ctx.send(embed=embed)
            
            # Send notification to Telegram
            message = f"✅ Discord user {ctx.author.name} has successfully verified their Telegram account!"
            await self._send_telegram_message(message)
        else:
            await ctx.send("❌ Invalid verification code! Please try again.")
    
    @telegram.command(name='status')
    async def status(self, ctx):
        """Check Telegram link status"""
        if ctx.author.id not in self.telegram_links:
            await ctx.send("❌ No Telegram account linked. Use `!telegram link <phone_number>` to start.")
            return
        
        link_info = self.telegram_links[ctx.author.id]
        
        embed = discord.Embed(
            title="📱 Telegram Link Status",
            color=discord.Color.blue()
        )
        embed.add_field(name="📞 Phone Number", value=f"`{link_info['phone']}`", inline=False)
        embed.add_field(name="✓ Verification", value=
            "✅ Verified" if link_info.get('verified') else "⏳ Pending",
            inline=False
        )
        
        if not link_info.get('verified'):
            embed.add_field(name="📋 Action Required", value=
                "Use `!telegram verify <code>` to complete verification",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @telegram.command(name='unlink')
    async def unlink(self, ctx):
        """Unlink your Telegram account"""
        if ctx.author.id in self.telegram_links:
            phone = self.telegram_links[ctx.author.id]['phone']
            del self.telegram_links[ctx.author.id]
            await ctx.send(f"✅ Successfully unlinked Telegram account ({phone})")
            
            message = f"Discord user {ctx.author.name} has unlinked their Telegram account."
            await self._send_telegram_message(message)
        else:
            await ctx.send("❌ You don't have a Telegram account linked!")
    
    @telegram.command(name='send')
    async def send(self, ctx, *, message: str):
        """Send a message to linked Telegram account"""
        if ctx.author.id not in self.telegram_links:
            await ctx.send("❌ You must link a Telegram account first! Use `!telegram link <phone_number>`")
            return
        
        link_info = self.telegram_links[ctx.author.id]
        
        if not link_info.get('verified'):
            await ctx.send("❌ Your Telegram account is not yet verified! Use `!telegram verify <code>`")
            return
        
        phone = link_info['phone']
        full_message = f"📨 From Discord ({ctx.author.name}):\n\n{message}"
        
        success = await self._send_telegram_message(full_message)
        if success:
            await ctx.send(f"✅ Message sent to Telegram ({phone})!")
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
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

async def setup(bot):
    await bot.add_cog(Telegram(bot))
