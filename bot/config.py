import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    MONGODB_URI = os.getenv("MONGODB_URI")
    CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
    OWNER_ID = int(os.getenv("OWNER_ID"))
    ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
    
    # Database collections
    FILES_COLLECTION = "files"
    BATCH_COLLECTION = "batches"
    USERS_COLLECTION = "users"
    
    # Messages
    START_MSG = """
<b>📦 Welcome to Premium File Store Bot!</b>

Store and share your files permanently with ease.

<b>✨ Features:</b>
• 📤 Batch file upload & storage
• 🔗 Instant shareable links
• 🆔 User ID lookup
• 💚 Always online

<b>🔐 Access:</b>
Only authorized admins can upload files.

Send /help for more information.
"""
    
    HELP_MSG = """
<b>📚 How to Use:</b>

<b>📤 Upload Files:</b>
• Send files directly to the bot
• Use /batch to start batch upload

<b>🔗 Generate Links:</b>
• Files are automatically stored
• Get links with /getlink [file_id]

<b>📊 Admin Commands:</b>
• /stats - View bot statistics
• /users - List all users
• /batch - Start batch upload
• /addadmin - Add new admin
• /removeadmin - Remove admin
• /broadcast - Send message to all users

<b>ℹ️ User Commands:</b>
• /start - Start the bot
• /help - Show this help
• /id - Get your user ID
• /getlink - Get file link
• /alive - Check bot status
"""
