from pymongo import MongoClient
from datetime import datetime
import uuid
from bot.config import Config

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client["telegram_file_store"]
        self.files = self.db[Config.FILES_COLLECTION]
        self.batches = self.db[Config.BATCH_COLLECTION]
        self.users = self.db[Config.USERS_COLLECTION]
    
    async def add_user(self, user_id, username=None, first_name=None):
        """Add or update user"""
        user = await self.get_user(user_id)
        if not user:
            return self.users.insert_one({
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "join_date": datetime.now(),
                "last_activity": datetime.now()
            })
        else:
            return self.users.update_one(
                {"user_id": user_id},
                {"$set": {"last_activity": datetime.now()}}
            )
    
    async def get_user(self, user_id):
        """Get user data"""
        return self.users.find_one({"user_id": user_id})
    
    async def save_file(self, file_data):
        """Save file metadata"""
        file_data["file_id"] = str(uuid.uuid4())
        file_data["created_at"] = datetime.now()
        file_data["downloads"] = 0
        return self.files.insert_one(file_data)
    
    async def get_file(self, file_id):
        """Get file by ID"""
        return self.files.find_one({"file_id": file_id})
    
    async def get_files_by_batch(self, batch_id):
        """Get all files in a batch"""
        return list(self.files.find({"batch_id": batch_id}))
    
    async def create_batch(self, user_id, name=None):
        """Create a new batch"""
        batch_data = {
            "batch_id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": name or f"Batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now(),
            "file_count": 0
        }
        self.batches.insert_one(batch_data)
        return batch_data
    
    async def update_batch(self, batch_id, increment=1):
        """Update batch file count"""
        return self.batches.update_one(
            {"batch_id": batch_id},
            {"$inc": {"file_count": increment}}
        )
    
    async def increment_downloads(self, file_id):
        """Increment download count"""
        return self.files.update_one(
            {"file_id": file_id},
            {"$inc": {"downloads": 1}}
        )
    
    async def get_stats(self):
        """Get bot statistics"""
        total_users = self.users.count_documents({})
        total_files = self.files.count_documents({})
        total_batches = self.batches.count_documents({})
        total_downloads = self.files.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$downloads"}}}
        ])
        total_downloads = list(total_downloads)
        total_downloads = total_downloads[0]["total"] if total_downloads else 0
        
        return {
            "total_users": total_users,
            "total_files": total_files,
            "total_batches": total_batches,
            "total_downloads": total_downloads
        }
