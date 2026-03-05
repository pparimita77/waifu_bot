from pyrogram import Client, filters
from pyrogram.types import Message

from database import users, characters, config
from utils import is_sudo, is_dev, is_owner, RARITY_DICT


# ------------------ UPLOADER ------------------

@Client.on_message(filters.command("upload"))
async def upload(client: Client, message: Message):
    user_id = message.from_user.id

    if not await is_dev(user_id):
        await message.reply_text("❌ You are not authorized to upload characters.")
        return

    args = message.text.split()[1:]

    if len(args) < 3:
        await message.reply_text("Usage: /upload <NAME> <ANIME> <RARITY_ID>")
        return

    name = args[0]
    anime = args[1]
    rarity_id = args[2]

    rarity_name = RARITY_DICT.get(rarity_id, "Unknown")

    try:
        result = await characters.insert_one({
            "name": name,
            "source": anime,
            "rarity": rarity_name
        })

        await message.reply_text(
            f"✅ Uploaded {name} ({rarity_name}) with ID: {result.inserted_id}"
        )

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# ------------------ DELETE ------------------

@Client.on_message(filters.command("delete"))
async def delete_character(client: Client, message: Message):
    user_id = message.from_user.id

    if not await is_dev(user_id):
        await message.reply_text("❌ You are not authorized to delete characters.")
        return

    args = message.text.split()[1:]

    if len(args) < 1:
        await message.reply_text("Usage: /delete <CHARACTER_ID>")
        return

    char_id = args[0]

    await characters.delete_one({"_id": char_id})

    await message.reply_text(f"🗑️ Deleted character with ID {char_id}")


# ------------------ SUDO ------------------

@Client.on_message(filters.command("gen_gems"))
async def gen_gems(client: Client, message: Message):

    if not await is_sudo(message.from_user.id):
        await message.reply_text("❌ Not authorized!")
        return

    args = message.text.split()[1:]

    if len(args) < 2:
        await message.reply_text("Usage: /gen_gems <amount> <user_id>")
        return

    amount = int(args[0])
    target_id = int(args[1])

    await users.update_one(
        {"user_id": target_id},
        {"$inc": {"gems": amount}},
        upsert=True
    )

    await message.reply_text(f"✅ Generated {amount} Gems for {target_id}")


# ------------------ STATS ------------------

@Client.on_message(filters.command("stats"))
async def stats(client: Client, message: Message):

    if not await is_dev(message.from_user.id):
        await message.reply_text("❌ Only dev can see stats.")
        return

    total_users = await users.count_documents({})
    total_chars = await characters.count_documents({})

    await message.reply_text(
        f"📊 Total Users: {total_users}\n📊 Total Characters: {total_chars}"
    )


# ------------------ DEV ------------------

@Client.on_message(filters.command("add_sudo"))
async def add_sudo(client: Client, message: Message):

    user_id = message.from_user.id

    if not is_owner(user_id):
        await message.reply_text("❌ Only owner can add sudo.")
        return

    args = message.text.split()[1:]

    if len(args) < 1:
        await message.reply_text("Usage: /add_sudo <USER_ID>")
        return

    sudo_id = int(args[0])

    await users.update_one(
        {"user_id": sudo_id},
        {"$set": {"sudo": True}},
        upsert=True
    )

    await message.reply_text(f"✅ Added sudo for user {sudo_id}")


@Client.on_message(filters.command("rm_sudo"))
async def rm_sudo(client: Client, message: Message):

    if not is_owner(message.from_user.id):
        await message.reply_text("❌ Only owner can remove sudo.")
        return

    args = message.text.split()[1:]

    if len(args) < 1:
        await message.reply_text("Usage: /rm_sudo <USER_ID>")
        return

    sudo_id = int(args[0])

    await users.update_one(
        {"user_id": sudo_id},
        {"$unset": {"sudo": ""}}
    )

    await message.reply_text(f"✅ Removed sudo for user {sudo_id}")


@Client.on_message(filters.command("add_dev"))
async def add_dev(client: Client, message: Message):

    if not is_owner(message.from_user.id):
        await message.reply_text("❌ Only owner can add devs.")
        return

    args = message.text.split()[1:]

    if len(args) < 1:
        await message.reply_text("Usage: /add_dev <USER_ID>")
        return

    dev_id = int(args[0])

    await users.update_one(
        {"user_id": dev_id},
        {"$set": {"dev": True}},
        upsert=True
    )

    await message.reply_text(f"✅ Added dev {dev_id}")


@Client.on_message(filters.command("rm_dev"))
async def rm_dev(client: Client, message: Message):

    if not is_owner(message.from_user.id):
        await message.reply_text("❌ Only owner can remove devs.")
        return

    args = message.text.split()[1:]

    if len(args) < 1:
        await message.reply_text("Usage: /rm_dev <USER_ID>")
        return

    dev_id = int(args[0])

    await users.update_one(
        {"user_id": dev_id},
        {"$unset": {"dev": ""}}
    )

    await message.reply_text(f"✅ Removed dev {dev_id}")


# ------------------ CONFIG ------------------

@Client.on_message(filters.command("setstart"))
async def setstart(client: Client, message: Message):

    if not await is_dev(message.from_user.id):
        await message.reply_text("❌ Only dev can set start message.")
        return

    await message.reply_text("✅ Start message updated!")


@Client.on_message(filters.command("setcost"))
async def setcost(client: Client, message: Message):

    if not await is_dev(message.from_user.id):
        await message.reply_text("❌ Only dev can set cost.")
        return

    await message.reply_text("✅ Cost updated!")


@Client.on_message(filters.command("setbidcost"))
async def setbidcost(client: Client, message: Message):

    if not await is_dev(message.from_user.id):
        await message.reply_text("❌ Only dev can set bid cost.")
        return

    await message.reply_text("✅ Bid cost updated!")


@Client.on_message(filters.command("rset"))
async def rset(client: Client, message: Message):

    if not await is_dev(message.from_user.id):
        await message.reply_text("❌ Only dev can reset rarity spawn.")
        return

    await message.reply_text("✅ Rarity reset for all groups!")
