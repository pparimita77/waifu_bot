import os
import logging
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID 
from database import db, users, set_premium, characters

# --- Configuration & Globals ---
settings_col = db['settings']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@Client.on_message(group=-1) # Group -1 ensures this runs before other commands
async def update_names_globally(client, message):
    if message.from_user:
        await users.update_one(
            {"_id": message.from_user.id},
            {"$set": {
                "first_name": message.from_user.first_name,
                "username": message.from_user.username,
                "last_chat_id": message.chat.id # Helps with Group Leaderboard
            }},
            upsert=True
        )

async def sync_database_on_start():
    try:
        await characters.update_many(
            {"rarity": {"$regex": "AMV", "$options": "i"}},
            {"$set": {"is_video": True}}
        )
        await characters.update_many(
            {"rarity": {"$not": {"$regex": "AMV", "$options": "i"}}},
            {"$set": {"is_video": False}}
        )
        print("✅ VPS Video Support: Database Synced.")
    except Exception as e:
        logger.error(f"Sync Error: {e}")

async def check_auction_end(client):
    while True:
        try:
            auc = await db.auctions.find_one({"_id": "active"})
            if auc and datetime.utcnow() >= auc['expiry']:
                winner_id = auc.get('bidder_id')
                
                if winner_id:
                    # Final payment check
                    amount = auc['current_bid']
                    res = await users.update_one(
                        {"_id": winner_id, "emeralds": {"$gte": amount}}, 
                        {"$inc": {"emeralds": -amount}}
                    )
                    
                    if res.modified_count > 0:
                        # Give the character to the winner
                        await db.user_collection.update_one(
                            {"_id": winner_id},
                            {"$push": {"characters": {"id": auc['char_id'], "rarity": auc['rarity']}}},
                            upsert=True
                        )
                        
                        msg = (
                            f"🎊 **AUCTION ENDED!**\n\n"
                            f"🏆 **Winner:** {auc['current_bidder']}\n"
                            f"💰 **Price:** {amount} Emeralds\n"
                            f"🎭 **Character:** {auc['name']}\n\n"
                            "Character added to your collection!"
                        )
                    else:
                        msg = f"❌ Auction Failed: {auc['current_bidder']} no longer has enough emeralds."
                else:
                    msg = f"⌛ Auction for **{auc['name']}** expired with no bidders."

                await client.send_message(auc['chat_id'], msg)
                await db.auctions.delete_one({"_id": "active"})

        except Exception as e:
            print(f"Auction Monitor Error: {e}")
        await asyncio.sleep(30)

async def check_premium_expiry(client):
    while True:
        try:
            now = datetime.now()
            expired_users = users.find({"is_premium": True, "premium_expiry": {"$lt": now}})
            async for user in expired_users:
                u_id = user["_id"]
                await users.update_one({"_id": u_id}, {"$set": {"is_premium": False}})
                try:
                    await client.send_message(u_id, "⚠️ <b>Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ᴇxᴘɪʀᴇᴅ!</b>")
                except: pass
            await asyncio.sleep(3600) 
        except Exception as e:
            await asyncio.sleep(60)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="TomiokaGiyuBot",
            api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN,
            plugins=dict(root="handlers") 
        )

    async def start(self):
        await super().start()
        await sync_database_on_start()
        asyncio.create_task(check_premium_expiry(self))
        print("✅ Tomioka Giyu Grabber Bot is Online!")

app = Bot()

# Owner commands stay here
@app.on_message(filters.command("spawnrate") & filters.user(OWNER_ID))
async def set_global_spawnrate(client, message):
    new_rate = message.command[1]
    await settings_col.update_one({"_id": "global_config"}, {"$set": {"spawn_rate": int(new_rate)}}, upsert=True)
    await message.reply_text(f"✅ Spawn Rate set to: {new_rate}")

if __name__ == "__main__":
    app.run()