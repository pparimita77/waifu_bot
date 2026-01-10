import sys
import traceback
import io
from pyrogram import Client, filters
from sudo import is_owner # MANDATORY: Only Owner

@Client.on_message(filters.command("eval") & is_owner)
async def evaluate_code(client, message):
    if len(message.command) < 2:
        return await message.reply_text("💻 **Usᴀɢᴇ:** `/eval <ᴘʏᴛʜᴏɴ_ᴄᴏᴅᴇ>`")

    status_msg = await message.reply_text("⌛ **Eᴠᴀʟᴜᴀᴛɪɴɢ...**")
    
    # Get the code from the message
    code = message.text.split(None, 1)[1]
    
    # Setup to capture the output of the code
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        # Define local variables available to the eval command
        # You can add 'db', 'users', etc., here to use them in Telegram
        from database import users, characters, claims
        
        async def aexec(code, client, message):
            exec(
                f"async def __aexec(client, message): " +
                "".join(f"\n {l}" for l in code.split("\n")),
            )
            return await locals()["__aexec"](client, message)

        await aexec(code, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = f"❌ **Eʀʀᴏʀ:**\n`{exc}`"
    elif stderr:
        evaluation = f"⚠️ **Sᴛᴅᴇʀʀ:**\n`{stderr}`"
    elif stdout:
        evaluation = f"✅ **Oᴜᴛᴘᴜᴛ:**\n`{stdout}`"
    else:
        evaluation = "✅ **Sᴜᴄᴄᴇss (Nᴏ Oᴜᴛᴘᴜᴛ)**"

    # If the output is too long for Telegram (4096 chars), send as file
    if len(evaluation) > 4000:
        with io.BytesIO(str.encode(evaluation)) as out_file:
            out_file.name = "eval_output.txt"
            await message.reply_document(document=out_file, caption="📄 **Oᴜᴛᴘᴜᴛ ᴛᴏᴏ ʟᴏɴɢ, sᴇɴᴛ ᴀs ғɪʟᴇ.**")
            await status_msg.delete()
    else:
        await status_msg.edit_text(evaluation)