# Discord Bot

A Python Discord bot built with discord.py

## Features
- Command handling
- Event listeners
- Extensible cog system

## Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```
DISCORD_TOKEN=your_bot_token_here
```

4. Run the bot:
```bash
python bot.py
```

## Project Structure
- `bot.py` — Main bot entry point
- `cogs/` — Command modules (organized features)
- `requirements.txt` — Python dependencies
- `.env` — Environment variables (keep this private!)

## Creating Commands

Commands are organized into "cogs" (modules). Example:

```python
# cogs/hello.py
from discord.ext import commands

class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.name}!")

async def setup(bot):
    await bot.add_cog(Hello(bot))
```

## Getting Your Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and click "Add Bot"
4. Copy the token and add it to `.env`
5. Enable necessary intents in "Bot" settings
6. Invite bot to your server via OAuth2 URL generator

## Contact

- **Email:** dankwahstephen389@gmail.com
- **WhatsApp:** +233 0542635388

## License
MIT
