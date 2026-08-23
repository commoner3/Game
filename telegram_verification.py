import os
import secrets
import sqlite3
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DB_FILE = "verification_sessions.db"

class TelegramVerification:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.bot = Bot(token=self.bot_token)
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing verification sessions"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER UNIQUE,
                session_id TEXT UNIQUE,
                verification_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_verified INTEGER DEFAULT 0,
                verified_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER UNIQUE,
                telegram_username TEXT,
                session_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def generate_codes(self):
        """Generate a session ID and verification code"""
        session_id = secrets.token_urlsafe(16)
        verification_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        return session_id, verification_code
    
    def create_verification_session(self, telegram_user_id):
        """Create a new verification session for a user"""
        session_id, verification_code = self.generate_codes()
        expires_at = datetime.now() + timedelta(minutes=15)
        
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Delete any existing pending sessions for this user
            cursor.execute(
                "DELETE FROM verification_sessions WHERE telegram_user_id = ? AND is_verified = 0",
                (telegram_user_id,)
            )
            
            # Create new session
            cursor.execute("""
                INSERT INTO verification_sessions 
                (telegram_user_id, session_id, verification_code, expires_at)
                VALUES (?, ?, ?, ?)
            """, (telegram_user_id, session_id, verification_code, expires_at))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created verification session for user {telegram_user_id}")
            return session_id, verification_code, expires_at
        
        except sqlite3.IntegrityError:
            logger.error(f"User {telegram_user_id} already has a session")
            return None, None, None
    
    def verify_code(self, telegram_user_id, verification_code):
        """Verify the code entered by the user"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, verification_code, expires_at, is_verified
                FROM verification_sessions
                WHERE telegram_user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (telegram_user_id,))
            
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, "No verification session found"
            
            session_id, stored_code, expires_at, is_verified = result
            
            # Check if already verified
            if is_verified:
                conn.close()
                return False, "This session is already verified"
            
            # Check if expired
            if datetime.fromisoformat(expires_at) < datetime.now():
                cursor.execute(
                    "DELETE FROM verification_sessions WHERE telegram_user_id = ? AND is_verified = 0",
                    (telegram_user_id,)
                )
                conn.commit()
                conn.close()
                return False, "Verification code expired. Please request a new one."
            
            # Check if code matches
            if verification_code == stored_code:
                # Mark as verified
                cursor.execute("""
                    UPDATE verification_sessions
                    SET is_verified = 1, verified_at = CURRENT_TIMESTAMP
                    WHERE telegram_user_id = ?
                """, (telegram_user_id,))
                
                conn.commit()
                conn.close()
                return True, f"Verified! Session ID: {session_id}"
            else:
                conn.close()
                return False, "Incorrect verification code"
        
        except Exception as e:
            logger.error(f"Error verifying code: {e}")
            return False, "An error occurred during verification"
    
    def get_user_session(self, telegram_user_id):
        """Get active session for a user"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, is_verified, verified_at
                FROM verification_sessions
                WHERE telegram_user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (telegram_user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[1] == 1:  # is_verified
                return result[0]  # session_id
            return None
        
        except Exception as e:
            logger.error(f"Error getting user session: {e}")
            return None


class TelegramBot:
    def __init__(self):
        self.verification = TelegramVerification()
        self.application = Application.builder().token(self.verification.bot_token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup bot command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("verify", self.verify_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        telegram_id = user.id
        
        # Create verification session
        session_id, verification_code, expires_at = self.verification.create_verification_session(telegram_id)
        
        if not session_id:
            await update.message.reply_text(
                "❌ You already have an active verification session. Please verify that first.\n"
                "Use /help for instructions."
            )
            return
        
        message = (
            f"🎮 **Game Bot Verification**\n\n"
            f"Your 6-digit verification code:\n"
            f"`{verification_code}`\n\n"
            f"⏱️ This code expires in 15 minutes.\n\n"
            f"📋 Your Session ID:\n"
            f"`{session_id}`\n\n"
            f"👉 Enter the verification code in the game to complete setup.\n\n"
            f"**Steps:**\n"
            f"1. Enter verification code: `{verification_code}`\n"
            f"2. Copy your session ID: `{session_id}`\n"
            f"3. Paste it in the game to activate your account"
        )
        
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"Sent verification code to user {telegram_id}")
    
    async def verify_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /verify command - user enters code here"""
        user = update.effective_user
        telegram_id = user.id
        
        if not context.args:
            await update.message.reply_text(
                "Please provide your verification code.\n"
                "Usage: `/verify 123456`",
                parse_mode="Markdown"
            )
            return
        
        verification_code = context.args[0]
        success, message = self.verification.verify_code(telegram_id, verification_code)
        
        if success:
            await update.message.reply_text(
                f"✅ {message}\n\n"
                f"Your account is now verified and ready to use!",
                parse_mode="Markdown"
            )
            logger.info(f"User {telegram_id} successfully verified")
        else:
            await update.message.reply_text(
                f"❌ {message}",
                parse_mode="Markdown"
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "🎮 **Game Bot Help**\n\n"
            "**Available Commands:**\n\n"
            "`/start` - Generate a new verification code and session ID\n"
            "`/verify <code>` - Verify your 6-digit code\n"
            "`/help` - Show this help message\n\n"
            "**How to activate your account:**\n"
            "1. Send `/start` to get your verification code\n"
            "2. Send `/verify <your-code>` to verify (replace with your 6-digit code)\n"
            "3. Copy your Session ID from the start message\n"
            "4. Enter the Session ID in the game to activate your bot"
        )
        
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        user = update.effective_user
        
        await update.message.reply_text(
            f"Hi {user.first_name}! 👋\n\n"
            f"I'm a game verification bot. Use /help to see available commands."
        )
    
    def run(self):
        """Start the bot"""
        logger.info("Starting Telegram bot...")
        self.application.run_polling()


# API Functions for game integration
def get_session_by_id(session_id):
    """Get verification status by session ID"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT is_verified, verified_at, telegram_user_id
            FROM verification_sessions
            WHERE session_id = ?
        """, (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == 1:  # is_verified
            return {
                "valid": True,
                "verified_at": result[1],
                "telegram_user_id": result[2]
            }
        return {"valid": False}
    
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        return {"valid": False}


def verify_session(session_id):
    """Verify a session ID is valid and verified"""
    session = get_session_by_id(session_id)
    return session.get("valid", False)


if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
