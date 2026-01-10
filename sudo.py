import asyncio
from pyrogram import filters
from config import OWNER_ID
from database import staff

# 1. Define the DEV_USERS list 
# Replace these numbers with actual Telegram IDs. 
# Even if empty [], it must exist to prevent errors.
DEV_USERS = [8325139144, 7987799736] 

# 2. Role Check Helper
async def check_staff_role(user_id, allowed_roles):
    """
    Checks if a user has permission based on the staff collection.
    Owner and Dev list users always return True.
    """
    # Owner and Devs bypass database checks
    if user_id == OWNER_ID or user_id in DEV_USERS:
        return True
        
    # Check roles stored in MongoDB
    user = await staff.find_one({"_id": user_id})
    if user and user.get("role") in allowed_roles:
        return True
    return False

# --- CUSTOM FILTERS ---

# Filter for Owner only (The person who has the config ID)
is_owner = filters.create(
    lambda _, __, m: bool(m.from_user and m.from_user.id == OWNER_ID)
)

# Filter for Devs (Owner + Manual Dev List in this file)
is_dev = filters.create(
    lambda _, __, m: bool(m.from_user and (m.from_user.id == OWNER_ID or m.from_user.id in DEV_USERS))
)

# Filter for Sudos (Owner + Dev + Any user promoted to 'sudo' or 'dev' in DB)
async def sudo_filter(_, __, m):
    if not m.from_user:
        return False
    return await check_staff_role(m.from_user.id, ["dev", "sudo"])

is_sudo = filters.create(sudo_filter)

# Filter for Uploaders (Owner + Dev + Any user promoted to 'uploader' in DB)
async def uploader_filter(_, __, m):
    if not m.from_user:
        return False
    return await check_staff_role(m.from_user.id, ["dev", "uploader"])

is_uploader = filters.create(uploader_filter)