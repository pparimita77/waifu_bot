import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import config

async def check():
    client = AsyncIOMotorClient(config.MONGO_URL)
    # List all databases on your cluster
    dbs = await client.list_database_names()
    print("📋 YOUR DATABASES FOUND:")
    for name in dbs:
        db = client[name]
        user_count = await db.users.count_documents({})
        char_count = await db.characters.count_documents({})
        print(f"🔹 Database: {name} | Users: {user_count} | Characters: {char_count}")

asyncio.run(check())