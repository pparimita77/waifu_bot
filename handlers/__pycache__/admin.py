from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import characters, shop_items
from sudo import is_dev  # Ensure this filter is imported

@Client.on_message(filters.command("addshop") & is_dev)
async def add_shop_admin(client, message):
    # 1. Check if the user provided arguments
    if len(message.command) < 3:
        return await message.reply_text("📝 **Usage:** `/addshop <char_id> <price>`")

    char_id = message.command[1]
    price_str = message.command[2]

    # 2. Validate Price is a number
    if not price_str.isdigit():
        return await message.reply_text("❌ Price must be a numerical value.")
    
    price = int(price_str)

    # 3. Find the character in the 'characters' collection
    char = await characters.find_one({"id": char_id})
    
    if not char:
        return await message.reply_text(f"❌ Character ID `{char_id}` not found in Database!")

    # 4. Prepare the setup message
    text = (
        f"🛒 **Sʜᴏᴘ Cᴏɴғɪɢᴜʀᴀᴛɪᴏɴ**\n\n"
        f"🌷 **Name:** {char['name']}\n"
        f"💰 **Price:** {price:,}\n\n"
        f"Select the currency for this item:"
    )

    buttons = [[
        InlineKeyboardButton("💎 Gᴇᴍs", callback_data=f"setshop_gems_{char_id}_{price}"),
        InlineKeyboardButton("🌟 Sᴛᴀʀᴅᴜsᴛ", callback_data=f"setshop_stardust_{char_id}_{price}")
    ]]

    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))