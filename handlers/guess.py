import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import characters, db

# --- SETTINGS ---
SUPPORT_CHAT_ID = -1003375783400 
SUPPORT_LINK = "https://t.me/Tomioka_Supportcore"
# ----------------

active_guesses = {}

async def update_guesser_stats(user_id, stardust_amount):
    """Updates both Stardust and the Guesser Leaderboard count."""
    await db.users.update_one(
        {"$or": [{"_id": user_id}, {"user_id": user_id}]},
        {
            "$inc": {
                "stardust": stardust_amount,
                "guesses": 1  # This feeds your new Leaderboard!
            }
        },
        upsert=True
    )

async def spawn_guess_character(client, chat_id):
    """Function to fetch and send a character. Returns True if successful."""
    pipeline = [{"$sample": {"size": 1}}]
    results = await characters.aggregate(pipeline).to_list(1)
    
    if not results:
        return False

    char = results[0]
    
    # IMPROVED: Check all possible image keys
    media_id = char.get('file_id') or char.get('img_url') or char.get('image') or char.get('photo')
    
    if not media_id:
        print(f"⚠️ Character {char['name']} has no media ID!")
        return False

    # Initialize or update round data
    current_round = active_guesses.get(chat_id, {}).get("loop_count", 0) + 1
    
    active_guesses[chat_id] = {
        "name": char['name'].lower().strip(),
        "display_name": char['name'],
        "file_id": media_id,
        "is_video": char.get("is_video", False) or "AMV" in str(char.get('rarity', '')).upper(),
        "active": True,
        "loop_count": current_round
    }

    caption = (
        "✨ <b>A mysterious waifu has appeared…</b> ✨\n\n"
        "<b>Can you guess her name correctly?</b> 💕\n\n"
        "<b>Type fast, guess smart~</b> 💭💫\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 <b>Round:</b> {current_round}\n"
    )

    try:
        if active_guesses[chat_id]["is_video"]:
            await client.send_video(chat_id, video=media_id, caption=caption)
        else:
            await client.send_photo(chat_id, photo=media_id, caption=caption)
        
        # Start the 20s countdown
        asyncio.create_task(start_timeout_timer(client, chat_id, current_round))
        return True
    except Exception as e:
        print(f"❌ Guess Spawn Error: {e}")
        active_guesses.pop(chat_id, None)
        return False

async def start_timeout_timer(client, chat_id, current_round):
    """Waits 20s. If round is still same and active, game ends."""
    await asyncio.sleep(20)
    if chat_id in active_guesses and active_guesses[chat_id]["active"]:
        if active_guesses[chat_id]["loop_count"] == current_round:
            name = active_guesses[chat_id]["display_name"]
            active_guesses[chat_id]["active"] = False
            await client.send_message(chat_id, f"⏰ <b>Tɪᴍᴇ's ᴜᴘ!</b>\n\nNo one guessed correctly. The character was: <b>{name}</b>\n\n<i>Game Over. Use /guess to start again!</i>")
            active_guesses.pop(chat_id, None)

@Client.on_message(filters.command("guess"))
async def start_guess_command(client, message: Message):
    chat_id = message.chat.id

    if chat_id != SUPPORT_CHAT_ID:
        return await message.reply_text(
            "❌ <b>Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ᴏᴜʀ Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴊᴏɪɴ sᴜᴘᴘᴏʀᴛ ᴄᴏʀᴇ 💎", url=SUPPORT_LINK)]])
        )

    if chat_id in active_guesses and active_guesses[chat_id]["active"]:
        return await message.reply_text("⏳ <b>A game is already running!</b>")

    active_guesses[chat_id] = {"loop_count": 0}
    success = await spawn_guess_character(client, chat_id)
    if not success:
        await message.reply_text("❌ Database error.")

@Client.on_message(filters.text & filters.group & ~filters.bot, group=1)
async def check_guess_answer(client, message: Message):
    chat_id = message.chat.id
    if chat_id != SUPPORT_CHAT_ID or chat_id not in active_guesses or not active_guesses[chat_id].get("active"):
        return

    user_answer = message.text.lower().strip()
    game_data = active_guesses[chat_id]
    name_parts = game_data["name"].split()
    
    # Check for full name or any part of the name
    if user_answer == game_data["name"] or user_answer in name_parts:
        # Mark current round as finished to prevent multiple winners
        active_guesses[chat_id]["active"] = False
        
        reward = random.randint(10, 50)
        # UPDATED: Increments 'guesses' count for the leaderboard
        await update_guesser_stats(message.from_user.id, reward)

        success_text = (
            f"🎉 <b>Cᴏʀʀᴇᴄᴛ! {message.from_user.mention} ᴡᴏɴ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <b>Cʜᴀʀᴀᴄᴛᴇʀ:</b> {game_data['display_name']}\n"
            f"💰 <b>Eᴀʀɴᴇᴅ:</b> <code>{reward}</code> Sᴛᴀʀᴅᴜsᴛ\n"
            f"🏆 <b>Tᴏᴛᴀʟ Wɪɴs:</b> (Cʜᴇᴄᴋ ɪɴ <code>/top</code>)\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await message.reply_text(success_text)
        
        # WAIT 2 SECONDS THEN START NEXT ROUND AUTOMATICALLY
        await asyncio.sleep(2)
        await spawn_guess_character(client, chat_id)
