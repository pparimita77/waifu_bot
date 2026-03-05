import asyncio
import random
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import users, characters, claims

# --- CONFIGURATION ---
SUPPORT_CHAT_ID = -1003375783400  
SUPPORT_LINK = "https://t.me/Tomioka_Supportcore"
ALLOWED_RARITIES = ["Common", "Legendary", "Rare"]

@Client.on_message(filters.command("marry") & filters.group)
async def marry_waifu(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    now = datetime.now()
    
    # 1. Group Restriction Check with Auto-Delete
    if chat_id != SUPPORT_CHAT_ID:
        warn = await message.reply_text(
            "⚠️ **Access Denied!**\n\n"
            "Marriage is only allowed in our **Support Chat**.\n"
            "Go there to try your luck with the dice!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Join Support Chat", url=SUPPORT_LINK)]
            ])
        )
        await asyncio.sleep(30)
        try:
            await warn.delete()
            await message.delete()
        except:
            pass
        return

    # 2. Fetch User Data
    user_data = await users.find_one({"$or": [{"_id": user_id}, {"user_id": user_id}]}) or {}
    last_marry = user_data.get("last_marry_time")
    spam_count = user_data.get("marry_spam_count", 0)
    
    COOLDOWN_NORMAL = timedelta(minutes=30)
    COOLDOWN_PENALTY = timedelta(hours=1)

    # 3. Check Cooldown Logic
    if last_marry and isinstance(last_marry, datetime):
        is_penalized = spam_count >= 2
        current_wait = COOLDOWN_PENALTY if is_penalized else COOLDOWN_NORMAL
        
        if now < last_marry + current_wait:
            new_spam_count = spam_count + 1
            await users.update_one(
                {"$or": [{"_id": user_id}, {"user_id": user_id}]},
                {"$inc": {"marry_spam_count": 1}}
            )
            
            remaining = (last_marry + current_wait) - now
            mins = int(remaining.total_seconds() // 60)
            
            warning = "⚠️ **STOP SPAMMING!** Your cooldown is now **1 hour**." if new_spam_count >= 3 else ""
            return await message.reply_text(
                f"⏳ **Cooldown!**\nRemaining: **{mins} minutes**.\n{warning}"
            )

# 4. Success Path: Pick Bride
    # We update the user's cooldown immediately to prevent "double-marry" exploits
    await users.update_one(
        {"$or": [{"_id": user_id}, {"user_id": user_id}]},
        {"$set": {"last_marry_time": now, "marry_spam_count": 0}},
        upsert=True
    )

    # Clean regex to match start of rarity string
    rarity_pattern = f"^({'|'.join(ALLOWED_RARITIES)})"
    query = {"rarity": {"$regex": rarity_pattern, "$options": "i"}}
    
    pipeline = [{"$match": query}, {"$sample": {"size": 1}}]
    random_chars = await characters.aggregate(pipeline).to_list(1)
    
    if not random_chars:
        return await message.reply_text("❌ No eligible brides found in the database!")

    char = random_chars[0]

    # 5. Dice Animation
    dice_msg = await client.send_dice(message.chat.id, emoji="🎲")
    await asyncio.sleep(4) # Wait for dice to stop rolling
    dice_value = dice_msg.dice.value

    # 6. Result Logic
    is_video = "amv" in str(char.get('rarity', '')).lower()
    media_id = char.get("file_id") or char.get("img_url") or char.get("image") or char.get("photo")

    if dice_value >= 4:
        # Success: Add to collection
        await claims.insert_one({
            "user_id": user_id,
            "char_id": char['id'],
            "name": char['name'],
            "rarity": char['rarity'],
            "anime": char.get('anime') or char.get('source', 'Unknown'),
            "date": now
        })

        bonus_text = ""
        if dice_value == 6:
            bonus_amount = 500 # Adjusted for "Jackpot" feel
            await users.update_one(
                {"$or": [{"_id": user_id}, {"user_id": user_id}]}, 
                {"$inc": {"stardust": bonus_amount}} # Using stardust to match your other scripts
            )
            bonus_text = f"\n\n🎁 **JACKPOT!** Rolled a 6!\nReceived **{bonus_amount:,} Stardust** ✨"

        text = (
            f"🎲 **Dice Rolled: {dice_value}**\n\n"
            "🌸 **Marriage Successful!** 🌸\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🎉 {message.from_user.mention}, you married a new waifu!\n"
            f"✨ **{char['name']}** added to harem.\n\n"
            f"💫 **Rarity:** {char['rarity']}\n"
            f"🎬 **Source:** {char.get('anime') or 'Unknown'}"
            f"{bonus_text}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
    else:
        text = (
            f"🎲 **Dice Rolled: {dice_value}**\n\n"
            f"💔 **{char['name']}** rejected your proposal!\n"
            "<i>Don't give up! Try again in 30 minutes.</i>"
        )

    # 7. Final Response with Video/Photo Support
    try:
        if not media_id:
            raise ValueError("No media found")
            
        if is_video:
            await message.reply_video(media_id, caption=text)
        else:
            await message.reply_photo(media_id, caption=text)
    except Exception:
        await message.reply_text(text)
