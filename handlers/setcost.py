from pyrogram import Client, filters  # <--- THIS WAS MISSING
from config import DEVS               # <--- ENSURE THIS IS HERE TOO
from database import characters        # Assuming you're updating character costs

@Client.on_message(filters.command("setcost") & filters.user(DEVS))
async def set_shop_cost(_, message):
    # /setcost <rarity_id> <min> <max>
    args = message.command
    if len(args) < 4:
        return await message.reply("Usᴀɢᴇ: `/setcost 4 5000 7000` (ID 4 = Special)")
    
    r_id, r_min, r_max = args[1], int(args[2]), int(args[3])
    
    if r_id in RARITY_MAP:
        RARITY_MAP[r_id]['min_shop'] = r_min
        RARITY_MAP[r_id]['max_shop'] = r_max
        await message.reply(f"✅ Updated {RARITY_MAP[r_id]['name']} range to {r_min}-{r_max}")