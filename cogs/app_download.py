import discord
from discord.ext import commands
import aiohttp

class AppDownload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Sample app database - replace with actual API
        self.apps_database = {
            'discord': {
                'name': 'Discord',
                'version': '1.0.190',
                'size': '85MB',
                'description': 'Talk, chat, hang out. Discord is where communities thrive.',
                'download_url': 'https://discord.com/download'
            },
            'python': {
                'name': 'Python',
                'version': '3.11.0',
                'size': '25MB',
                'description': 'A programming language that lets you work quickly',
                'download_url': 'https://www.python.org/downloads/'
            },
            'vscode': {
                'name': 'Visual Studio Code',
                'version': '1.76.0',
                'size': '64MB',
                'description': 'Code editor redefined and optimized for building modern web and cloud applications',
                'download_url': 'https://code.visualstudio.com/download'
            },
            'ffmpeg': {
                'name': 'FFmpeg',
                'version': '6.0',
                'size': '45MB',
                'description': 'A complete, cross-platform solution to record, convert and stream audio and video.',
                'download_url': 'https://ffmpeg.org/download.html'
            }
        }
    
    @commands.group(name='app')
    async def app(self, ctx):
        """Application download commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `!app download`, `!app search`, or `!app list`")
    
    @app.command(name='download')
    async def app_download(self, ctx, *, app_name: str):
        """Download application by name"""
        app_name_lower = app_name.lower()
        
        if app_name_lower in self.apps_database:
            app_info = self.apps_database[app_name_lower]
            
            embed = discord.Embed(
                title=f"📥 {app_info['name']}",
                description=app_info['description'],
                color=discord.Color.green()
            )
            embed.add_field(name="📦 Version", value=app_info['version'], inline=True)
            embed.add_field(name="💾 Size", value=app_info['size'], inline=True)
            embed.add_field(
                name="🔗 Download Link",
                value=f"[Click here to download]({app_info['download_url']})",
                inline=False
            )
            embed.set_footer(text="Downloaded links are opening in browser")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ App `{app_name}` not found. Use `!app list` to see available apps.")
    
    @app.command(name='search')
    async def app_search(self, ctx, *, query: str):
        """Search for applications"""
        query_lower = query.lower()
        results = [
            app for app_name, app in self.apps_database.items()
            if query_lower in app_name or query_lower in app['name'].lower() or query_lower in app['description'].lower()
        ]
        
        if not results:
            await ctx.send(f"❌ No apps found matching: `{query}`")
            return
        
        embed = discord.Embed(
            title=f"🔍 Search Results for '{query}'",
            color=discord.Color.blue(),
            description=f"Found {len(results)} app(s):\n"
        )
        
        for app_data in results[:5]:
            embed.add_field(
                name=f"📱 {app_data['name']}",
                value=f"{app_data['description'][:100]}...\n*Version: {app_data['version']} | Size: {app_data['size']}*",
                inline=False
            )
        
        if len(results) > 5:
            embed.description += f"\n... and {len(results) - 5} more"
        
        await ctx.send(embed=embed)
    
    @app.command(name='list')
    async def app_list(self, ctx):
        """List available applications"""
        embed = discord.Embed(
            title="📱 Available Applications",
            color=discord.Color.blue(),
            description="Use `!app download <name>` to download\n"
        )
        
        for app_name, app_info in self.apps_database.items():
            embed.add_field(
                name=f"📦 {app_info['name']}",
                value=f"v{app_info['version']} | {app_info['size']}\n`!app download {app_name}`",
                inline=True
            )
        
        embed.set_footer(text=f"Total apps: {len(self.apps_database)}")
        await ctx.send(embed=embed)
    
    @app.command(name='info')
    async def app_info(self, ctx, *, app_name: str):
        """Get detailed information about an app"""
        app_name_lower = app_name.lower()
        
        if app_name_lower in self.apps_database:
            app_info = self.apps_database[app_name_lower]
            
            embed = discord.Embed(
                title=f"ℹ️ {app_info['name']} - Detailed Info",
                description=app_info['description'],
                color=discord.Color.purple()
            )
            embed.add_field(name="📦 Version", value=app_info['version'])
            embed.add_field(name="💾 Size", value=app_info['size'])
            embed.add_field(
                name="🔗 Download",
                value=f"[Official Download]({app_info['download_url']})",
                inline=False
            )
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ App `{app_name}` not found.")

async def setup(bot):
    await bot.add_cog(AppDownload(bot))
