import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from database import shop_items, users, claims

@Client.on_message(filters.command("shop"))
async def character_shop(client, message):
    # Fetch all items manually added by admin
    items = await shop_items.find().to_list(length=None)
    
    if not items:
        return await message.reply_text("🙇 Sʜᴏᴘ Is Cᴜʀʀᴇɴᴛʟʏ Eᴍᴘᴛʏ!")

    # For this version, we show the first item. 
    # You can add pagination logic later if you have many items.
    char = items[0] 
    currency = char.get("currency", "stardust")
    emoji = "💎" if currency == "gems" else "🌟"

    text = (
        f"🙇 **Iʀᴀssʜᴀɪᴍᴀsᴇ - '{message.from_user.first_name}' Sᴀɴ** ✨\n\n"
        f"🌷 **Nᴀᴍᴇ:** {char['name']}\n"
        f"🛍 **Iᴅ:** <code>{char['id']}</code>\n"
        f"🧭 **Sᴏᴜʀᴄᴇ:** {char['anime']}\n"
        f"💰 **Cᴏsᴛ:** {emoji} <code>{char['price']:,}</code> {currency.capitalize()}"
    )

    buttons = [
        [
            InlineKeyboardButton("⬅️", callback_data="shop_prev"),
            InlineKeyboardButton("🛒 BUY", callback_data=f"buy_shop_{char['id']}"),
            InlineKeyboardButton("➡️", callback_data="shop_next")
        ]
    ]
    
    await message.reply_photo(
        photo=char['file_id'],
        caption=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^buy_shop_"))
async def buy_handler(client, query):
    user_id = query.from_user.id
    char_id = query.data.split("_")[2]

    item = await shop_items.find_one({"id": char_id})
    if not item:
        return await query.answer("❌ Item not found!", show_alert=True)

    currency = item.get("currency", "stardust")
    price = item["price"]
    
    user_data = await users.find_one({"_id": user_id}) or {}
    user_balance = user_data.get(currency, 0)

    if user_balance < price:
        emoji = "💎" if currency == "gems" else "🌟"
        return await query.answer(f"❌ You need {price - user_balance} more {emoji}!", show_alert=True)

    # Deduct Balance & Add Character
    await users.update_one({"_id": user_id}, {"$inc": {currency: -price}})
    await claims.insert_one({
        "user_id": user_id,
        "char_id": item["id"],
        "name": item["name"],
        "anime": item["anime"],
        "rarity": item["rarity"]
    })

    await query.message.edit_caption(
        caption=f"🎉 **Pᴜʀᴄʜᴀsᴇ Sᴜᴄᴄᴇssғᴜʟ!**\n\nYou bought **{item['name']}**!",
        reply_markup=None
    )