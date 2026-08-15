import os
import hashlib
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def generate_file_hash(file_path):
    """Generate hash for file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def format_size(size_bytes):
    """Format file size to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def get_progress_bar(percentage, length=20):
    """Create progress bar"""
    filled = int(length * percentage // 100)
    bar = '█' * filled + '░' * (length - filled)
    return f"[{bar}] {percentage:.1f}%"

def create_file_buttons(file_id):
    """Create inline keyboard for file"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Download File", callback_data=f"download_{file_id}")],
        [InlineKeyboardButton("🔗 Share Link", callback_data=f"share_{file_id}")],
        [InlineKeyboardButton("📊 Stats", callback_data=f"stats_{file_id}")]
    ])

def is_admin(user_id):
    """Check if user is admin"""
    from bot.config import Config
    return user_id == Config.OWNER_ID or user_id in Config.ADMIN_IDS
