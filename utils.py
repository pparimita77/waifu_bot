from pyrogram.errors import UserNotParticipant, ChatAdminRequired, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from config import OWNER_ID, DEVS
from database import staff

# --- CONFIGURATION ---
AUTH_CHANNEL = "@Tomioka_Supportcore"

# --- AUTHORIZATION LISTS ---
OWNERS = [OWNER_ID] if not isinstance(OWNER_ID, list) else OWNER_ID
DEVELOPERS = DEVS if isinstance(DEVS, list) else ([DEVS] if DEVS else [])

# --- PERMISSION CHECKS ---
async def is_owner(user_id: int) -> bool:
    return user_id in OWNERS

async def is_dev(user_id: int) -> bool:
    if user_id in OWNERS or user_id in DEVELOPERS:
        return True
    user = await staff.find_one({"_id": user_id})
    return user is not None and user.get("role") in ["dev", "sudo"]

async def is_sudo(user_id: int) -> bool:
    if user_id in OWNERS or user_id in DEVELOPERS:
        return True
    user = await staff.find_one({"_id": user_id})
    return user is not None and user.get("role") in ["sudo", "dev"]

# --- FORCESUB LOGIC ---
async def is_subscribed(client, user_id):
    try:
        await client.get_chat_member(AUTH_CHANNEL, user_id)
        return True
    except UserNotParticipant:
        return False
    except (ChatAdminRequired, RPCError):
        return True 
    except Exception:
        return True

# ALIAS for check_join (to fix your user.py error)
check_join = is_subscribed

async def send_join_message(client, message):
    channel_url = f"https://t.me/{AUTH_CHANNEL.replace('@', '')}"
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Jᴏɪɴ Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ", url=channel_url)],
        [InlineKeyboardButton("🔄 Tʀʏ Aɢᴀɪɴ", url=f"https://t.me/{client.me.username}?start=check")]
    ])
    text = "❌ <b>Aᴄᴄᴇss Dᴇɴɪᴇᴅ!</b>\nYᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴏᴜʀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ."
    
    if hasattr(message, "reply_text"):
        await message.reply_text(text, reply_markup=buttons, parse_mode=ParseMode.HTML)
    else:
        await message.answer(text.replace("<b>", "").replace("</b>", ""), show_alert=True)

# --- RARITY DATA ---
RARITY_DICT = {
    "1": "Common ⚪️", "2": "Legendary 💮", "3": "Rare 🍁", 
    "4": "Special 🫧", "5": "Limited 🔮", "6": "Celestial 🎐",
    "7": "Manga 🔖", "8": "Expensive 💸", "9": "Demonic ☠",
    "10": "Royal 👑", "11": "Summer 🏝️", "12": "Winter ❄️",
    "13": "Valentine 💝", "14": "Seasonal 🍂", "15": "Halloween 🎃",
    "16": "Christmas 🎄", "17": "AMV 🎥"
}

# --- PLACEHOLDERS (To prevent future crashes) ---
async def is_premium(user_id: int):
    # Returns False for everyone by default until you add premium logic
    return False

async def get_random_char():
    # Placeholder for your random character logic
    pass