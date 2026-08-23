import discord
from discord.ext import commands
import yt_dlp
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH', './downloads')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 500))  # MB

# Create download directory if it doesn't exist
Path(DOWNLOAD_PATH).mkdir(parents=True, exist_ok=True)

class MediaDownload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }
    
    @commands.group(name='music')
    async def music(self, ctx):
        """Music download commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `!music download <url>` or `!music playlist <url>`")
    
    @music.command(name='download')
    async def music_download(self, ctx, url: str):
        """Download audio from YouTube"""
        async with ctx.typing():
            try:
                await ctx.send(f"🎵 Downloading audio from: {url}")
                
                ydl_opts = self.ydl_opts.copy()
                ydl_opts['format'] = 'bestaudio/best'
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
                    
                    if file_size > MAX_FILE_SIZE:
                        os.remove(filename)
                        await ctx.send(f"❌ File too large ({file_size:.2f}MB). Max: {MAX_FILE_SIZE}MB")
                        return
                    
                    await ctx.send(f"✅ Downloaded: **{info.get('title', 'Unknown')}**")
                    await ctx.send(f"📁 File size: {file_size:.2f}MB")
                    
                    # Try to send file if it's not too large for Discord
                    if file_size < 25:  # Discord free tier limit
                        try:
                            await ctx.send(file=discord.File(filename))
                        except:
                            await ctx.send(f"File saved to: `{filename}`")
            except Exception as e:
                await ctx.send(f"❌ Error downloading: {str(e)}")
    
    @music.command(name='playlist')
    async def music_playlist(self, ctx, url: str):
        """Download entire YouTube playlist"""
        async with ctx.typing():
            try:
                await ctx.send(f"🎵 Downloading playlist from: {url}")
                
                ydl_opts = self.ydl_opts.copy()
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['outtmpl'] = os.path.join(DOWNLOAD_PATH, 'Playlist', '%(playlist_title)s', '%(title)s.%(ext)s')
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    playlist_title = info.get('title', 'Playlist')
                    
                    await ctx.send(f"✅ Downloaded playlist: **{playlist_title}**")
                    await ctx.send(f"📁 Total entries: {len(info.get('entries', []))}")
            except Exception as e:
                await ctx.send(f"❌ Error downloading playlist: {str(e)}")
    
    @commands.group(name='movie')
    async def movie(self, ctx):
        """Movie download commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `!movie download <title>` or `!movie search <query>`")
    
    @movie.command(name='download')
    async def movie_download(self, ctx, *, title: str):
        """Download movie by title (simulated - requires API)"""
        async with ctx.typing():
            await ctx.send(f"🎬 Searching for movie: **{title}**")
            await ctx.send("⚠️ Movie download requires an API key (TMDB or similar)")
            await ctx.send("📝 Please configure your movie download API in `.env`")
    
    @movie.command(name='search')
    async def movie_search(self, ctx, *, query: str):
        """Search for movies"""
        async with ctx.typing():
            await ctx.send(f"🔍 Searching for movies related to: **{query}**")
            await ctx.send("⚠️ Movie search requires an API key (TMDB or similar)")
    
    @commands.group(name='picture')
    async def picture(self, ctx):
        """Picture download commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `!picture download <url>`")
    
    @picture.command(name='download')
    async def picture_download(self, ctx, url: str):
        """Download picture from URL"""
        async with ctx.typing():
            try:
                await ctx.send(f"🖼️ Downloading image from: {url}")
                
                import aiohttp
                from PIL import Image
                import io
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            image_data = await resp.read()
                            
                            # Validate it's an image
                            try:
                                Image.open(io.BytesIO(image_data))
                                
                                # Save image
                                filename = os.path.join(DOWNLOAD_PATH, f'image_{ctx.author.id}.png')
                                with open(filename, 'wb') as f:
                                    f.write(image_data)
                                
                                file_size = len(image_data) / (1024 * 1024)
                                await ctx.send(f"✅ Downloaded image ({file_size:.2f}MB)")
                                
                                if file_size < 8:  # Discord free tier
                                    await ctx.send(file=discord.File(filename))
                            except:
                                await ctx.send("❌ Invalid image file")
                        else:
                            await ctx.send(f"❌ Failed to download (Status: {resp.status})")
            except Exception as e:
                await ctx.send(f"❌ Error downloading image: {str(e)}")
    
    @picture.command(name='gallery')
    async def picture_gallery(self, ctx):
        """View download gallery"""
        try:
            files = os.listdir(DOWNLOAD_PATH)
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            
            if not image_files:
                await ctx.send("📁 No images in gallery")
                return
            
            embed = discord.Embed(title="📁 Picture Gallery", color=discord.Color.blue())
            embed.description = f"Total images: {len(image_files)}\n\n"
            
            for img in image_files[:10]:  # Show first 10
                embed.description += f"🖼️ {img}\n"
            
            if len(image_files) > 10:
                embed.description += f"\n... and {len(image_files) - 10} more"
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error loading gallery: {str(e)}")

async def setup(bot):
    await bot.add_cog(MediaDownload(bot))
