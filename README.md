# Discord Bot

A Python Discord bot built with discord.py with support for Telegram linking, media downloads, and more.

## Features
- Command handling
- Event listeners
- Extensible cog system
- **Telegram Integration** - Link Discord to Telegram with phone number verification
- **Music Download** - Download audio from YouTube and other platforms
- **Movie Download** - Download movies with metadata
- **Picture Download** - Download and manage images
- **App Download** - Share and download applications

## Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/commoner3/Game.git
   cd Game
   ```

2. Create virtual environment (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory:
   ```
   DISCORD_TOKEN=your_bot_token_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_telegram_chat_id_here
   DOWNLOAD_PATH=./downloads
   MAX_FILE_SIZE=500
   ```

5. Run the bot:
   ```bash
   python bot.py
   ```

## Project Structure
- `bot.py` — Main bot entry point
- `cogs/` — Command modules (organized features)
  - `hello.py` — Basic hello and ping commands
  - `telegram.py` — Telegram integration with phone verification
  - `media_download.py` — Music, movie, and picture downloads
  - `app_download.py` — Application download management
- `requirements.txt` — Python dependencies
- `.env` — Environment variables (keep this private!)
- `.env.example` — Environment variables template

## Available Commands

### Basic Commands
- `!hello` — Say hello to the user
- `!ping` — Check bot latency

### Telegram Integration (with Phone Verification)
- `!telegram link <phone_number>` — Start linking with your phone number (e.g., +233542635388)
  - Generates a 6-digit verification code
  - Code is valid for 10 minutes
  - Send the code to your Telegram bot
- `!telegram verify <code>` — Verify with the code sent to your phone
- `!telegram status` — Check Telegram link status
- `!telegram send <message>` — Send message to linked Telegram account
- `!telegram unlink` — Unlink your Telegram account

### Music Downloads
- `!music download <url>` — Download audio from YouTube
- `!music playlist <url>` — Download entire playlist

### Movie Downloads
- `!movie download <title>` — Download movie by title
- `!movie search <query>` — Search for movies

### Picture Downloads
- `!picture download <url>` — Download picture from URL
- `!picture gallery` — View download gallery

### App Downloads
- `!app download <app_name>` — Download application
- `!app search <query>` — Search for apps
- `!app list` — List available applications
- `!app info <app_name>` — Get app details

## Telegram Setup Guide

### Step 1: Create a Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the steps to create your bot
4. Copy the API token and add it to `.env` as `TELEGRAM_BOT_TOKEN`

### Step 2: Get Your Chat ID
1. Send a message to your newly created bot
2. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Look for `"chat":{"id":XXXXX}` and copy the ID
4. Add it to `.env` as `TELEGRAM_CHAT_ID`

### Step 3: Link Your Discord Account
1. In Discord, use: `!telegram link +1234567890` (replace with your actual phone number)
   - Phone number format: `+[country code][number]`
   - Examples:
     - Ghana: `+233542635388`
     - USA: `+12025551234`
     - UK: `+442071838750`
2. Bot will generate a 6-digit verification code
3. Send this code to your Telegram bot
4. Return to Discord and use: `!telegram verify 123456` (replace with actual code)
5. ✅ Account linked and verified!

### Step 4: Start Using
- Check status: `!telegram status`
- Send messages: `!telegram send Hello from Discord!`
- Unlink anytime: `!telegram unlink`

## Telegram Verification Process

```
Discord User
    ↓
!telegram link +233542635388
    ↓
Bot generates code: 123456 (10 min expiry)
    ↓
User sends code to Telegram bot
    ↓
User verifies: !telegram verify 123456
    ↓
✅ Account verified and linked
```

## Creating Custom Commands

Commands are organized into "cogs" (modules). Example:

```python
# cogs/example.py
from discord.ext import commands

class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def example(self, ctx):
        await ctx.send(f"Example command!")

async def setup(bot):
    await bot.add_cog(Example(bot))
```

## Getting Your Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and click "Add Bot"
4. Copy the token and add it to `.env`
5. Enable necessary intents in "Bot" settings:
   - Message Content Intent
   - Server Members Intent
   - Message Read State Intent
6. Invite bot to your server via OAuth2 URL generator with these permissions:
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History

## Configuration

Edit the following in `.env`:

```env
# Discord
DISCORD_TOKEN=your_discord_bot_token

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Media Download Settings (optional)
DOWNLOAD_PATH=./downloads
MAX_FILE_SIZE=500  # MB
```

## Requirements

- discord.py >= 2.3.2
- python-dotenv >= 1.0.0
- yt-dlp >= 2023.3.4 (for YouTube downloads)
- python-telegram-bot >= 20.0 (for Telegram integration)
- requests >= 2.28.0
- Pillow >= 9.0.0 (for image processing)
- aiohttp >= 3.8.4

## Troubleshooting

### Bot not responding
- Check that your `DISCORD_TOKEN` is correct in `.env`
- Ensure bot has necessary permissions in your Discord server
- Verify bot is running: `python bot.py`

### Telegram verification not working
- Ensure phone number starts with `+` (e.g., `+233542635388`)
- Check that `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are correct
- Verify code hasn't expired (10 minute limit)
- Make sure you've sent the code to your Telegram bot before verifying

### Downloads not working
- Verify `DOWNLOAD_PATH` exists or create it manually
- Check that yt-dlp is properly installed: `pip install --upgrade yt-dlp`
- Some URLs may be restricted or blocked

## Country Codes Reference

| Country | Code |
|---------|------|
| Ghana | +233 |
| USA | +1 |
| UK | +44 |
| Canada | +1 |
| Australia | +61 |
| India | +91 |
| Nigeria | +234 |
| South Africa | +27 |
| Kenya | +254 |
| Uganda | +256 |

## License
MIT

## Contact

- **Email:** dankwahstephen389@gmail.com
- **WhatsApp:** +233 0542635388
