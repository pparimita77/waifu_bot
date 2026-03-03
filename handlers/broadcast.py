import asyncio
import os
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, ChatWriteForbidden, ChatAdminRequired
from database import users, groups 
from config import OWNER_ID

def get_progress_bar(percentage):
    """Generates a visual progress bar"""
    completed = int(percentage / 10)
    remaining = 10 - completed
    return "🔹" * completed + "🔸" * remaining

@Client.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_msg(client, message):
    if not message.reply_to_message:
        return await message.reply_text("📢 **Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ɪᴛ.**")

    status_msg = await message.reply_text("🔍 **Fᴇᴛᴄʜɪɴɢ ᴀʟʟ IDs...**")
    
    # 1. Fetching all target IDs
    all_users = await users.find({}, {"_id": 1}).to_list(length=None)
    all_groups = await groups.find({}, {"_id": 1}).to_list(length=None)
    
    # Clean IDs and ensure they are integers
    user_ids = [int(u["_id"]) for u in all_users if str(u["_id"]).replace("-", "").isdigit()]
    group_ids = [int(g["_id"]) for g in all_groups if str(g["_id"]).replace("-", "").isdigit()]
    
    targets = list(set(user_ids + group_ids))
    total_targets = len(targets)
    
    if total_targets == 0:
        return await status_msg.edit_text("❌ **Dᴀᴛᴀʙᴀsᴇ ɪs ᴇᴍᴘᴛʏ!**")

    await status_msg.edit_text(f"🚀 **Bʀᴏᴀᴅᴄᴀsᴛ Sᴛᴀʀᴛᴇᴅ...**\n**Tᴏᴛᴀʟ Tᴀʀɢᴇᴛs:** `{total_targets}`")

    success = 0
    blocked = 0
    failed = 0
    done = 0
    failed_ids = []

    # 2. Start Broadcast Loop
    for target_id in targets:
        try:
            await message.reply_to_message.copy(chat_id=target_id)
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_to_message.copy(chat_id=target_id)
                success += 1
            except:
                failed += 1
                failed_ids.append(f"ID: {target_id} | Reason: FloodWait Failure")
        except (UserIsBlocked, InputUserDeactivated):
            await users.delete_one({"_id": target_id})
            blocked += 1
        except (ChatWriteForbidden, ChatAdminRequired):
            await groups.delete_one({"_id": target_id})
            blocked += 1
        except Exception as e:
            failed += 1
            failed_ids.append(f"ID: {target_id} | Error: {str(e)}")
        
        done += 1

        # Progress Update every 10 users
        if done % 10 == 0 or done == total_targets:
            percentage = (done / total_targets) * 100
            bar = get_progress_bar(percentage)
            try:
                await status_msg.edit_text(
                    f"🚀 **Bʀᴏᴀᴅᴄᴀsᴛɪɴɢ...**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 **Pʀᴏɢʀᴇss:** {bar} `{percentage:.1f}%`\n"
                    f"✅ **Sᴇɴᴛ:** `{success}`\n"
                    f"🧹 **Cʟᴇᴀɴᴇᴅ:** `{blocked}`\n"
                    f"❌ **Fᴀɪʟᴇᴅ:** `{failed}`\n"
                    f"🔢 **ᴛᴏᴛᴀʟ:** `{done}/{total_targets}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━"
                )
            except:
                pass
        
        await asyncio.sleep(0.1)

    # 3. Final Result and Log Handling (UTF-8 Fixed)
    final_text = (
        f"✅ **Bʀᴏᴀᴅᴄᴀsᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ!**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ **Sᴜᴄᴄᴇssғᴜʟ:** `{success}`\n"
        f"🧹 **DB Pᴜʀɢᴇᴅ:** `{blocked}`\n"
        f"🛠️ **Uɴᴋɴᴏᴡɴ Fᴀɪʟs:** `{failed}`\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    if failed_ids:
        log_file = "broadcast_failed_log.txt"
        # encoding="utf-8" fixes the Windows error
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("BROADCAST FAILED LOG\n")
            f.write("━━━━━━━━━━━━━━━━━━━━\n")
            for line in failed_ids:
                f.write(f"{line}\n")
        
        try:
            await message.reply_document(document=log_file, caption="🛠️ **Broadcast Fail Log**")
        except:
            pass
        finally:
            if os.path.exists(log_file):
                os.remove(log_file)

    await status_msg.edit_text(final_text)