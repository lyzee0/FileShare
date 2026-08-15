from http.server import BaseHTTPRequestHandler
import json
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.main import app
from bot.config import Config

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read the webhook data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # Parse the update
            update = json.loads(post_data.decode('utf-8'))
            
            # Process the update asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create update object and process
            loop.run_until_complete(app.process_update(update))
            loop.close()
            
            # Send response
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            
        except Exception as e:
            print(f"Error processing update: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_GET(self):
        # Health check
        if self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive")
        else:
            self.send_response(404)
            self.end_headers()

# Initialize bot on startup
def init_bot():
    """Initialize bot connection"""
    try:
        # Set webhook
        webhook_url = os.getenv("VERCEL_URL", "").replace("https://", "")
        if webhook_url:
            webhook_url = f"https://{webhook_url}/webhook"
            asyncio.run(app.set_webhook(webhook_url))
            print(f"✅ Webhook set to: {webhook_url}")
    except Exception as e:
        print(f"⚠️ Webhook setup failed: {e}")

# Run initialization
init_bot()
