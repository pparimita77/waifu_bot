import asyncio
import re
import html
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from database import db, characters, users, claims, settings
from config import OWNER_ID, DEVS
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- INITIALIZE SCHEDULER ---
scheduler = AsyncIOScheduler()
scheduler.start()

# --- HELPERS ---
def parse_duration(duration_str):
    match = re.match(r"(\d+)(h|m|min|d)", duration_str.lower())
    if not match: return None
    value, unit = int(match.group(1)), match.group(2)
    if unit == 'd': return timedelta(days=value)
    if unit == 'h': return timedelta(hours=value)
    if unit in ['m', 'min']: return timedelta(minutes=value)
    return None

async def end_auction(client: Client, chat_id: int):
    auc = await db.auctions.find_one({"_id": "active"})
    if not auc: return

    winner_id = auc.get("bidder_id")
    bid_amount = auc.get("current_bid")
    char_id = auc.get("char_id")
    char_name = auc.get("name", "Unknown")

    if not winner_id or bid_amount == 0:
        await client.send_message(chat_id, f"✖️ **Auction Ended!**\nNo bids were placed for **{char_name}**.")
    else:
        # Cross-reference User ID in DB
        user = await users.find_one({"user_id": winner_id}) or await users.find_one({"_id": winner_id})
        
        if not user or user.get("emeralds", 0) < bid_amount:
            await client.send_message(chat_id, f"❌ **Auction Failed!**\nWinner {auc['current_bidder']} no longer has enough 💠.")
        else:
            # DEDUCT EMERALDS AND ADD TO HAREM
            await users.update_one({"_id": user["_id"]}, {"$inc": {"emeralds": -bid_amount}})
            await claims.insert_one({
                "user_id": winner_id, 
                "char_id": char_id, 
                "id": char_id,
                "date": datetime.utcnow()
            })
            
            safe_winner = html.escape(auc['current_bidder'])
            await client.send_message(
                chat_id, 
                f"🎊 AUCTION CLOSED! 🎊\n\n"
                f"👤 Winner: <a href='tg://user?id={winner_id}'>{safe_winner}</a>\n"
                f"💰 <b>Final Price:</b> {bid_amount:,} 💠\n"
                f"🌸 <b>{char_name}</b> has been added to their harem!",
                parse_mode=ParseMode.HTML
            )

    await db.auctions.delete_one({"_id": "active"})
    try:
        scheduler.remove_job("timer_job")
        scheduler.remove_job("auction_task")
    except: pass

async def timer_update(client, chat_id):
    auc = await db.auctions.find_one({"_id": "active"})
    if not auc: return
    
    # SAFETY: Force end if time is up
    if datetime.utcnow() >= auc['expiry']:
        return await end_auction(client, chat_id)

    if auc.get("msg_id"):
        await show_auction(client, chat_id, edit_id=auc["msg_id"])

# --- COMMANDS ---

# Create a single flat set of authorized IDs
AUTHORIZED = set()
if isinstance(OWNER_ID, list):
    AUTHORIZED.update(OWNER_ID)
else:
    AUTHORIZED.add(OWNER_ID)

if DEVS:
    AUTHORIZED.update(DEVS)

# Now use the AUTHORIZED set in your filter
@Client.on_message(filters.command("start_auction") & filters.user(list(AUTHORIZED)))
async def start_auction_cmd(client, message: Message):
    if len(message.command) < 4:
        return await message.reply("❌ Usage: `/start_auction ID PRICE TIME` (e.g. `1 5000 1h`)")

    char_id, start_price = message.command[1], int(message.command[2])
    duration = parse_duration(message.command[3])
    if not duration: return await message.reply("❌ Invalid time format!")

    char = await characters.find_one({"id": char_id})
    if not char: return await message.reply("❌ Character not found.")

    await settings.delete_one({"type": "daily_shop"})

    expiry = datetime.utcnow() + duration
    auction_data = {
        "char_id": char_id, 
        "name": char['name'], 
        "rarity": char['rarity'],
        "anime": char.get('anime') or char.get('animee', 'Unknown'),
        "file_id": char.get('file_id') or char.get('image'),
        "is_video": "amv" in char.get('rarity', '').lower() or char.get("is_video", False),
        "start_price": start_price, 
        "current_bid": 0, 
        "current_bidder": "None",
        "bidder_id": None, 
        "bidders_list": [],
        "expiry": expiry, 
        "msg_id": None
    }

    await db.auctions.update_one({"_id": "active"}, {"$set": auction_data}, upsert=True)
    
    scheduler.add_job(end_auction, "date", run_date=expiry, args=[client, message.chat.id], id="auction_task", replace_existing=True)
    scheduler.add_job(timer_update, "interval", seconds=10, args=[client, message.chat.id], id="timer_job", replace_existing=True)
    
    sent_msg = await show_auction(client, message.chat.id)
    if sent_msg:
        await db.auctions.update_one({"_id": "active"}, {"$set": {"msg_id": sent_msg.id}})

@Client.on_message(filters.command("auction"))
async def check_auction_cmd(client, message: Message):
    auc = await db.auctions.find_one({"_id": "active"})
    if not auc:
        return await message.reply("❌ No active auction at the moment.")
    await show_auction(client, message.chat.id)

@Client.on_message(filters.command("bid"))
async def place_bid(client, message: Message):
    auc = await db.auctions.find_one({"_id": "active"})
    if not auc: return await message.reply("❌ No active auction.")

    if len(message.command) < 2: return await message.reply("❌ Usage: `/bid Amount`")
    
    try:
        bid_amount = int(message.command[1])
    except: return await message.reply("❌ Enter a numeric amount!")

    user_id = message.from_user.id
    user_data = await users.find_one({"user_id": user_id}) or await users.find_one({"_id": user_id})
    
    if await claims.find_one({"user_id": user_id, "char_id": auc["char_id"]}):
        return await message.reply("⚠️ You already own this character!")

    if user_id not in ([OWNER_ID] + (DEVS or [])):
        if not user_data or user_data.get("emeralds", 0) < bid_amount:
            return await message.reply("❌ Not enough 💠 Emeralds!")

    min_required = auc['start_price'] if auc['current_bid'] == 0 else auc['current_bid'] + 1
    if bid_amount < min_required:
        return await message.reply(f"❌ Min bid: {min_required:,}")

    # ANTI-SNIPE: Extend if bid within last 60s
    now = datetime.utcnow()
    current_expiry = auc['expiry']
    time_left = (current_expiry - now).total_seconds()
    
    new_expiry = current_expiry
    if time_left < 60:
        new_expiry = now + timedelta(minutes=2)
        scheduler.add_job(end_auction, "date", run_date=new_expiry, args=[client, message.chat.id], id="auction_task", replace_existing=True)

    await db.auctions.update_one(
        {"_id": "active"},
        {
            "$set": {
                "current_bid": bid_amount, 
                "current_bidder": message.from_user.first_name, 
                "bidder_id": user_id, 
                "expiry": new_expiry 
            },
            "$addToSet": {"bidders_list": user_id}
        }
    )
    
    try: await message.delete()
    except: pass
    await show_auction(client, message.chat.id, edit_id=auc["msg_id"])

# Create a single flat set of authorized IDs
AUTHORIZED = set()
if isinstance(OWNER_ID, list):
    AUTHORIZED.update(OWNER_ID)
else:
    AUTHORIZED.add(OWNER_ID)

if DEVS:
    AUTHORIZED.update(DEVS)
    
@Client.on_message(filters.command("stop_auction") & filters.user(list(AUTHORIZED)))
async def stop_auction_cmd(client, message: Message):
    await db.auctions.delete_one({"_id": "active"})
    try:
        scheduler.remove_job("timer_job")
        scheduler.remove_job("auction_task")
    except: pass
    await message.reply("🛑 **Auction stopped and database cleared.**")

async def show_auction(client, chat_id, edit_id=None):
    auc = await db.auctions.find_one({"_id": "active"})
    if not auc: return
    
    now = datetime.utcnow()
    expiry = auc['expiry']
    remaining = expiry - now
    total_sec = int(remaining.total_seconds())
    
    # If time is up, prevent negative timer and force closure
    if total_sec <= 0:
        total_sec = 0
        if not edit_id: 
            return await end_auction(client, chat_id)

    h, r = divmod(total_sec, 3600)
    m, s = divmod(r, 60)
    
    next_min_bid = auc['current_bid'] + 1 if auc['current_bid'] > 0 else auc['start_price']
    total_bidders = len(auc.get("bidders_list", []))
    
    caption = (
        "🔨 <b>LIVE AUCTION ACTIVE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🎭 <b>Nᴀᴍᴇ:</b> {html.escape(auc['name'])}\n"
        f"📺 <b>Sᴇʀɪᴇꜱ:</b> {html.escape(auc['anime'])}\n"
        f"💫 <b>Rᴀʀɪᴛʏ:</b> {auc['rarity']}\n"
        f"💰 <b>Cᴜʀʀᴇɴᴛ Bɪᴅ:</b> {auc['current_bid']:,} 💠\n"
        f"⌛️ <b>Rᴇᴍᴀɪɴɪɴɢ:</b> <code>{h:02d}:{m:02d}:{s:02d}</code>\n"
        f"🎯 <b>Cᴜʀʀᴇɴᴛ Bɪᴅᴅᴇʀ:</b> {html.escape(auc['current_bidder'])}\n"
        f"👥 <b>Tᴏᴛᴀʟ Bɪᴅᴅᴇʀꜱ:</b> {total_bidders}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 Bid higher than {next_min_bid:,} 💠 using /bid"
    )

    try:
        if edit_id: 
            return await client.edit_message_caption(chat_id, edit_id, caption=caption, parse_mode=ParseMode.HTML)
        
        mode = client.send_video if auc.get("is_video") else client.send_photo
        return await mode(chat_id, auc['file_id'], caption=caption, parse_mode=ParseMode.HTML)
    except Exception: pass