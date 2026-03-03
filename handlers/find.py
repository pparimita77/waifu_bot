from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from database import characters

# Updated Map for all 17 Rarities
RARITY_MAP = {
    "Common": "Common ⚪️", 
    "Legendary": "Legendary 💮", 
    "Rare": "Rare 🍁",
    "Special": "Special 🫧", 
    "Limited": "Limited 🔮", 
    "Celestial": "Celestial 🎐",
    "Manga": "Manga 🔖", 
    "Expensive": "Expensive 💸", 
    "Demonic": "Demonic ☠",
    "Royal": "Royal 👑", 
    "Summer": "Summer 🏝️", 
    "Winter": "Winter ❄️",
    "Valentine": "Valentine 💝", 
    "Seasonal": "Seasonal 🍂", 
    "Halloween": "Halloween 🎃",
    "Christmas": "Christmas 🎄", 
    "AMV": "AMV 🎥"
}

def build_navigation_keyboard(query_name, page, total_pages):
    nav_row = []
    # Button 1: Previous
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Pʀᴇᴠɪᴏᴜs", callback_data=f"find_{query_name}_{page-1}"))
    
    # Button 2: Next
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Nᴇxᴛ ➡️", callback_data=f"find_{query_name}_{page+1}"))
    
    # If no navigation is possible, just show a Close button
    if not nav_row:
        nav_row.append(InlineKeyboardButton("🗑️ Cʟᴏsᴇ Mᴇɴᴜ", callback_data="lockclaim_close"))
        
    return InlineKeyboardMarkup([nav_row])

async def get_find_text(query_name, page=0):
    limit = 15 
    skip = page * limit
    
    # Search in BOTH 'name' and 'anime' fields
    search_query = {
        "$or": [
            {"name": {"$regex": query_name, "$options": "i"}},
            {"anime": {"$regex": query_name, "$options": "i"}}
        ]
    }
    
    total_count = await characters.count_documents(search_query)
    total_pages = (total_count + limit - 1) // limit

    if total_count == 0:
        return None, 0

    cursor = characters.find(search_query).skip(skip).limit(limit)
    results = await cursor.to_list(length=limit)

    response_text = f"🔍 **Sᴇᴀʀᴄʜ:** `{query_name}`\n"
    response_text += f"━━━━━━━━━━━━━━━━━━━━\n"
    
    for char in results:
        db_rarity = char.get("rarity", "Unknown")
        # Clean rarity name to handle strings like "Common ⚪️"
        clean_rarity = str(db_rarity).split(" ")[0].strip()
        display_rarity = RARITY_MAP.get(clean_rarity, db_rarity)
        
        response_text += (
            f"🌸 **{char['name']}** [`{char['id']}`]\n"
            f"📺 {char.get('anime', 'Unknown')} | {display_rarity}\n\n"
        )
    
    response_text += f"━━━━━━━━━━━━━━━━━━━━\n"
    response_text += f"📄 **Pᴀɢᴇ:** `{page+1}/{total_pages}` | **Tᴏᴛᴀʟ:** `{total_count}`"
    
    return response_text, total_pages

@Client.on_message(filters.command("find"))
async def find_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/find <name or anime>`")
    
    query_name = " ".join(message.command[1:])
    text, total_pages = await get_find_text(query_name, 0)
    
    if not text:
        return await message.reply_text(f"❌ **No results for:** `{query_name}`")
    
    await message.reply_text(
        text,
        reply_markup=build_navigation_keyboard(query_name, 0, total_pages),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex("^find_"))
async def find_callback(client, callback_query):
    data_parts = callback_query.data.split("_")
    # Using join in case the search query had underscores
    query_name = "_".join(data_parts[1:-1])
    page = int(data_parts[-1])
    
    text, total_pages = await get_find_text(query_name, page)
    
    if text:
        try:
            await callback_query.message.edit_text(
                text,
                reply_markup=build_navigation_keyboard(query_name, page, total_pages),
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass
    await callback_query.answer()