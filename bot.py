from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import yt_dlp
import os

TOKEN = os.getenv("8549179660:AAGRCyktSUi7MYTdvPzjPDRCTq3XWuZ0ivA")  # توکن رباتت رو توی Railway یا محیط اجرا بذار
CHANNEL_USERNAME = "@goodgirl_lingerie"  # یوزرنیم کانال تلگرام که باید عضو باشن

def start(update, context):
    user_id = update.message.from_user.id
    chat_member = context.bot.get_chat_member(CHANNEL_USERNAME, user_id)

    if chat_member.status in ["member", "administrator", "creator"]:
        update.message.reply_text("سلام! لینک ویدیو رو بفرست 🎬")
    else:
        update.message.reply_text(f"برای استفاده از ربات باید عضو کانال {CHANNEL_USERNAME} بشی.")

def get_formats(update, context):
    url = update.message.text
    try:
        with yt_dlp.YoutubeDL({'listformats': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
    except Exception as e:
        update.message.reply_text("خطا در گرفتن اطلاعات ویدیو ❌")
        return

    keyboard = []
    for f in formats:
        if f.get('format_note') and f.get('filesize'):
            kb_text = f"{f['format_note']} - {round(f['filesize']/1024/1024,1)}MB"
            keyboard.append([InlineKeyboardButton(kb_text, callback_data=f"{f['format_id']}|{url}")])

    if keyboard:
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("یکی از کیفیت‌ها رو انتخاب کن:", reply_markup=reply_markup)
    else:
        update.message.reply_text("کیفیت‌های قابل دانلود پیدا نشد ❌")

def button(update, context):
    query = update.callback_query
    format_id, url = query.data.split("|")
    query.answer()

    ydl_opts = {
        'format': format_id,
        'outtmpl': 'video.mp4'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        query.edit_message_text(text=f"دانلود با کیفیت {format_id} انجام شد ✅")
        # اینجا می‌تونی فایل رو با context.bot.send_document بفرستی
    except Exception as e:
        query.edit_message_text(text="خطا در دانلود ویدیو ❌")

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_formats))
dp.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()
