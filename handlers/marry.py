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

    # 4. Success Path: Update DB and Pick Bride
    await users.update_one(
        {"$or": [{"_id": user_id}, {"user_id": user_id}]},
        {"$set": {"last_marry_time": now, "marry_spam_count": 0}},
        upsert=True
    )

    query = {"rarity": {"$regex": f"^({'|'.join(ALLOWED_RARITIES)})", "$options": "i"}}
    pipeline = [{"$match": query}, {"$sample": {"size": 1}}]
    random_chars = await characters.aggregate(pipeline).to_list(1)
    
    if not random_chars:
        return await message.reply_text("❌ No eligible characters found!")

    char = random_chars[0]
    char_id = char['id']

    # 5. Dice Animation
    dice_msg = await client.send_dice(message.chat.id, emoji="🎲")
    await asyncio.sleep(4) 
    dice_value = dice_msg.dice.value

    # 6. Success/Failure Result
    if dice_value >= 4:
        # Save to claims
        await claims.insert_one({
            "user_id": user_id,
            "char_id": char['id'],
            "name": char['name'],
            "rarity": char['rarity'],
            "anime": char.get('anime') or char.get('animee', 'Unknown'),
            "date": now
        })

        # Jackpot Logic
        bonus_text = ""
        if dice_value == 6:
            bonus_amount = 10
            await users.update_one(
                {"$or": [{"_id": user_id}, {"user_id": user_id}]}, 
                {"$inc": {"emeralds": bonus_amount}}
            )
            bonus_text = f"\n\n🎁 **JACKPOT!** Rolled a 6!\nReceived **{bonus_amount:,} Emeralds** 💠"

        # Update User Harem
        await users.update_one(
            {"$or": [{"_id": user_id}, {"user_id": user_id}]}, 
            {"$push": {"married": char_id}}
        )
        
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
            f"💔 **{char['name']}** rejected you!\n"
            "<i>Try again in 30 minutes!</i>"
        )

    # 7. Final Response
    img = char.get("file_id") or char.get("image")
    try:
        await message.reply_photo(img, caption=text)
    except:
        await message.reply_text(text)