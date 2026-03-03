import config
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified
from database import get_disabled_claims, settings

# The standard list of 17 rarities
RARITIES = [
    "Common", "Legendary", "Rare", "Special", "Limited", "Celestial",
    "Manga", "Expensive", "Demonic", "Royal", "Summer", "Winter",
    "Valentine", "Seasonal", "Halloween", "Christmas", "AMV"
]

def build_rset_keyboard(disabled_list):
    buttons = []
    for i in range(0, len(RARITIES), 2):
        row = []
        k1 = RARITIES[i]
        s1 = "❌" if k1 in disabled_list else "✅"
        row.append(InlineKeyboardButton(f"{s1} {k1}", callback_data=f"lockclaim_{k1}"))
        
        if i + 1 < len(RARITIES):
            k2 = RARITIES[i+1]
            s2 = "❌" if k2 in disabled_list else "✅"
            row.append(InlineKeyboardButton(f"{s2} {k2}", callback_data=f"lockclaim_{k2}"))
        buttons.append(row)
    
    buttons.append([
        InlineKeyboardButton("🔓 Uɴʟᴏᴄᴋ Aʟʟ", callback_data="lockclaim_unlockall"),
        InlineKeyboardButton("🔒 Lᴏᴄᴋ Aʟʟ", callback_data="lockclaim_lockall")
    ])
    buttons.append([InlineKeyboardButton("🗑 Cʟᴏsᴇ Mᴇɴᴜ", callback_data="lockclaim_close")])
    return InlineKeyboardMarkup(buttons)

@Client.on_message(filters.command("rset") & filters.user(config.OWNER_ID))
async def rset_owner(client, message):
    disabled = await get_disabled_claims()
    await message.reply_text(
        "🚫 <b>Cʟᴀɪᴍ Rᴀʀɪᴛʏ Lᴏᴄᴋᴇʀ</b>\n"
        "Only ✅ rarities will appear in /claim.\n\n"
        "✅ = Cʟᴀɪᴍᴀʙʟᴇ | ❌ = Lᴏᴄᴋᴇᴅ",
        reply_markup=build_rset_keyboard(disabled)
    )

@Client.on_callback_query(filters.regex("^lockclaim_") & filters.user(config.OWNER_ID))
async def rset_callback(client, callback_query):
    data = callback_query.data.split("_")[1]
    
    if data == "close":
        return await callback_query.message.delete()

    current_doc = await settings.find_one({"_id": "claim_rarity_lock"}) or {"disabled": []}
    disabled = current_doc.get("disabled", [])

    if data == "unlockall":
        disabled = []
    elif data == "lockall":
        disabled = RARITIES[:]
    else:
        if data in disabled:
            disabled.remove(data)
        else:
            disabled.append(data)
    
    await settings.update_one(
        {"_id": "claim_rarity_lock"}, 
        {"$set": {"disabled": disabled}}, 
        upsert=True
    )
    
    try:
        await callback_query.message.edit_reply_markup(reply_markup=build_rset_keyboard(disabled))
        await callback_query.answer("Sᴇᴛᴛɪɴɢs Uᴘᴅᴀᴛᴇᴅ!")
    except MessageNotModified:
        await callback_query.answer("Already set!")