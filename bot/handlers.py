import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from bot.config import Config
from bot.database import Database
from bot.utils import is_admin, create_file_buttons, format_size

db = Database()

# Start Command
async def start_command(client, message: Message):
    user = message.from_user
    await db.add_user(user.id, user.username, user.first_name)
    
    await message.reply_text(
        Config.START_MSG,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 Help", callback_data="help"),
             InlineKeyboardButton("ℹ️ About", callback_data="about")]
        ])
    )

# Help Command
async def help_command(client, message: Message):
    await message.reply_text(Config.HELP_MSG)

# Alive Check
async def alive_command(client, message: Message):
    stats = await db.get_stats()
    await message.reply_text(
        f"<b>💚 Bot is Alive!</b>\n\n"
        f"📊 <b>Statistics:</b>\n"
        f"👥 Users: {stats['total_users']}\n"
        f"📁 Files: {stats['total_files']}\n"
        f"📦 Batches: {stats['total_batches']}\n"
        f"📥 Downloads: {stats['total_downloads']}\n\n"
        f"⚡ Status: Online\n"
        f"🤖 Version: 2.0.0"
    )

# Get User ID
async def id_command(client, message: Message):
    user_id = message.from_user.id
    await message.reply_text(f"<b>🆔 Your User ID:</b> <code>{user_id}</code>")

# File Upload Handler
async def file_upload_handler(client, message: Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.reply_text("❌ You don't have permission to upload files.")
        return
    
    # Handle different file types
    file_data = None
    file_type = None
    
    if message.document:
        file_data = message.document
        file_type = "document"
    elif message.photo:
        file_data = message.photo[-1]
        file_type = "photo"
    elif message.video:
        file_data = message.video
        file_type = "video"
    elif message.audio:
        file_data = message.audio
        file_type = "audio"
    else:
        await message.reply_text("❌ Unsupported file type!")
        return
    
    # Save file metadata
    file_info = {
        "file_name": getattr(file_data, "file_name", f"{file_type}_{message.id}"),
        "file_size": file_data.file_size,
        "file_type": file_type,
        "file_unique_id": file_data.file_unique_id,
        "file_id": file_data.file_id,
        "user_id": user_id,
        "batch_id": None
    }
    
    result = await db.save_file(file_info)
    file_id = result.inserted_id
    
    # Create link
    share_link = f"https://t.me/{client.me.username}?start=file_{file_id}"
    
    await message.reply_text(
        f"✅ <b>File Uploaded Successfully!</b>\n\n"
        f"📁 File: <code>{file_info['file_name']}</code>\n"
        f"📦 Size: {format_size(file_info['file_size'])}\n"
        f"🔗 Link: {share_link}\n\n"
        f"📋 File ID: <code>{file_id}</code>",
        reply_markup=create_file_buttons(str(file_id))
    )

# Get Link Command
async def getlink_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Please provide a file ID.\nUsage: /getlink file_id")
        return
    
    file_id = message.command[1]
    file_data = await db.get_file(file_id)
    
    if not file_data:
        await message.reply_text("❌ File not found!")
        return
    
    share_link = f"https://t.me/{client.me.username}?start=file_{file_id}"
    await message.reply_text(
        f"🔗 <b>File Link</b>\n\n"
        f"📁 {file_data['file_name']}\n"
        f"📦 Size: {format_size(file_data['file_size'])}\n\n"
        f"🔗 Link: {share_link}"
    )

# Batch Upload Command
async def batch_command(client, message: Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.reply_text("❌ You don't have permission to create batches.")
        return
    
    # Create batch
    batch = await db.create_batch(user_id)
    
    await message.reply_text(
        f"📦 <b>Batch Created!</b>\n\n"
        f"Batch ID: <code>{batch['batch_id']}</code>\n"
        f"Name: {batch['name']}\n\n"
        f"Send files to add them to this batch.\n"
        f"Use /addtobatch {batch['batch_id']} to add files."
    )

# Statistics Command (Admin only)
async def stats_command(client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ Admin only command!")
        return
    
    stats = await db.get_stats()
    await message.reply_text(
        f"📊 <b>Bot Statistics</b>\n\n"
        f"👥 Total Users: {stats['total_users']}\n"
        f"📁 Total Files: {stats['total_files']}\n"
        f"📦 Total Batches: {stats['total_batches']}\n"
        f"📥 Total Downloads: {stats['total_downloads']}"
    )

# Callback Handler
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    
    if data.startswith("download_"):
        file_id = data.split("_")[1]
        file_data = await db.get_file(file_id)
        
        if file_data:
            await db.increment_downloads(file_id)
            await callback_query.answer(f"Downloading {file_data['file_name']}")
            # Forward file from channel
            await client.copy_message(
                callback_query.message.chat.id,
                Config.CHANNEL_ID,
                int(file_data['file_id'])
            )
        else:
            await callback_query.answer("File not found!", show_alert=True)
    
    elif data.startswith("share_"):
        file_id = data.split("_")[1]
        file_data = await db.get_file(file_id)
        
        if file_data:
            share_link = f"https://t.me/{client.me.username}?start=file_{file_id}"
            await callback_query.message.reply_text(
                f"🔗 <b>Share Link</b>\n\n"
                f"{share_link}"
            )
    
    elif data == "help":
        await callback_query.message.reply_text(Config.HELP_MSG)
    
    elif data == "about":
        await callback_query.message.reply_text(
            "🤖 <b>Premium File Store Bot</b>\n\n"
            "Version: 2.0.0\n"
            "Built with Pyrogram\n"
            "Database: MongoDB\n\n"
            "© 2024 All Rights Reserved"
        )
