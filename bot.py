from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import yt_dlp
import os, asyncio

TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "goodgirl_lingerie"  # بدون @

async def start(update, context):
    user_id = update.message.from_user.id
    chat_member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)

    if chat_member.status in ["member", "administrator", "creator"]:
        await update.message.reply_text("سلام! لینک ویدیو رو بفرست 🎬")
    else:
        await update.message.reply_text(f"برای استفاده از ربات باید عضو کانال @{CHANNEL_USERNAME} بشی.")

async def get_formats(update, context):
    url = update.message.text
    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
    except Exception:
        await update.message.reply_text("خطا در گرفتن اطلاعات ویدیو ❌")
        return

    keyboard = []
    for f in formats:
        size = f.get("filesize") or f.get("filesize_approx")
        if f.get('format_note') and size:
            kb_text = f"{f['format_note']} - {round(size/1024/1024,1)}MB"
            keyboard.append([InlineKeyboardButton(kb_text, callback_data=f"{f['format_id']}|{url}")])

    if keyboard:
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("یکی از کیفیت‌ها رو انتخاب کن:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("کیفیت‌های قابل دانلود پیدا نشد ❌")

async def button(update, context):
    query = update.callback_query
    format_id, url = query.data.split("|")
    await query.answer()

    ydl_opts = {'format': format_id, 'outtmpl': 'video.mp4'}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await query.message.reply_video("video.mp4")
        await query.edit_message_text(text=f"دانلود با کیفیت {format_id} انجام شد ✅")
    except Exception:
        await query.edit_message_text(text="خطا در دانلود ویدیو ❌")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_formats))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()   # این خودش async رو هندل می‌کنه

if __name__ == "__main__":
    main()
