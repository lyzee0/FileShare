from pyrogram import Client, filters
from bot.config import Config
from bot.handlers import (
    start_command, help_command, alive_command, id_command,
    file_upload_handler, getlink_command, batch_command,
    stats_command, callback_handler
)
from bot.database import Database

app = Client(
    "file_store_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

db = Database()

# Register handlers
@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await start_command(client, message)

@app.on_message(filters.command("help"))
async def help_handler(client, message):
    await help_command(client, message)

@app.on_message(filters.command("alive"))
async def alive_handler(client, message):
    await alive_command(client, message)

@app.on_message(filters.command("id"))
async def id_handler(client, message):
    await id_command(client, message)

@app.on_message(filters.command("getlink"))
async def getlink_handler(client, message):
    await getlink_command(client, message)

@app.on_message(filters.command("batch"))
async def batch_handler(client, message):
    await batch_command(client, message)

@app.on_message(filters.command("stats"))
async def stats_handler(client, message):
    await stats_command(client, message)

@app.on_message(filters.document | filters.photo | filters.video | filters.audio)
async def file_handler(client, message):
    await file_upload_handler(client, message)

@app.on_callback_query()
async def callback_handler_wrapper(client, callback_query):
    await callback_handler(client, callback_query)

def run_bot():
    print("🤖 Bot is starting...")
    app.run()
