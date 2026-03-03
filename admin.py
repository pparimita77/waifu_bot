from pyrogram import filters
from bot import app
from config import OWNER_ID, DEV_IDS, SUDO_IDS, UPLOADER_IDS
from database import users, rarities

def is_owner(id): return id == OWNER_ID
def is_dev(id): return id in DEV_IDS or is_owner(id)

@app.on_message(filters.command("add_dev") & filters.user(OWNER_ID))
async def add_dev(_, m):
    DEV_IDS.append(int(m.command[1]))
    await m.reply("✅ Dev added")

@app.on_message(filters.command("rm_dev") & filters.user(OWNER_ID))
async def rm_dev(_, m):
    DEV_IDS.remove(int(m.command[1]))
    await m.reply("❌ Dev removed")

@app.on_message(filters.command("add_sudo") & filters.user(DEV_IDS))
async def add_sudo(_, m):
    SUDO_IDS.append(int(m.command[1]))
    await m.reply("✅ Sudo added")

@app.on_message(filters.command("rm_sudo") & filters.user(DEV_IDS))
async def rm_sudo(_, m):
    SUDO_IDS.remove(int(m.command[1]))
    await m.reply("❌ Sudo removed")

@app.on_message(filters.command("add_uploader") & filters.user(DEV_IDS))
async def add_uploader(_, m):
    UPLOADER_IDS.append(int(m.command[1]))
    await m.reply("✅ Uploader added")

@app.on_message(filters.command("rm_uploader") & filters.user(DEV_IDS))
async def rm_uploader(_, m):
    UPLOADER_IDS.remove(int(m.command[1]))
    await m.reply("❌ Uploader removed")

@app.on_message(filters.command("add_subscription") & filters.user(OWNER_ID))
async def add_sub(_, m):
    uid = int(m.command[1])
    days = int(m.command[2])
    users.update_one(
        {"_id": uid},
        {"$set": {"premium": True}},
        upsert=True
    )
    await m.reply("👑 Subscription added")
@app.on_message(filters.command("rm_subscription") & filters.user(OWNER_ID))
@app.on_message(filters.command("rm_subscription") & filters.user(OWNER_ID))
async def rm_sub(_, m):
    uid = int(m.command[1])
    users.update_one(
        {"_id": uid},
        {"$unset": {"premium": True}},
        upsert=True
    )
    await m.reply("👑 Subscription removed")