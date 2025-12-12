from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import yt_dlp
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = -1001402628553

async def start(update, context):
    user_id = update.message.from_user.id
    try:
        chat_member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
    except Exception:
        await update.message.reply_text("❌ خطا در بررسی عضویت کانال")
        return

    if chat_member.status in ["member", "administrator", "creator"]:
        welcome_text = (
            "🌸 خوش اومدی دوست عزیز!\n\n"
            "✨ اینجا می‌تونی لینک یوتیوب مورد علاقه حامد رو بفرستی و من برات دانلودش کنم.\n"
            "📽️ فقط کافیه لینک رو بفرستی و کیفیت مورد نظرت رو انتخاب کنی.\n\n"
            "💡 آماده‌ای؟ لینک رو بفرست 🎬"
        )
        await update.message.reply_text(welcome_text)
    else:
        keyboard = [[InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/goodgirl_lingerie")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🚪 برای استفاده از ربات باید عضو کانال بشی.\n"
            "👇 روی دکمه‌ی زیر بزن و عضو شو:",
            reply_markup=reply_markup
        )



async def get_formats(update, context):
    user_id = update.message.from_user.id
    try:
        chat_member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
    except Exception:
        await update.message.reply_text("خطا در بررسی عضویت کانال ❌")
        return

    if chat_member.status not in ["member", "administrator", "creator"]:
        await update.message.reply_text("برای استفاده از ربات باید عضو کانال بشی. همین الآن عضو شو : @goodgirl_lingerie")
        return

    # اگر عضو بود ادامه بده
    await update.message.reply_text("لینک ویدیو رو بفرست ...")
    url = update.message.text.strip()
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
            keyboard.append([InlineKeyboardButton(kb_text, callback_data=f"{f['format_id']}")])

    if keyboard:
        context.user_data['video_url'] = url
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("یکی از کیفیت‌ها رو انتخاب کن:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("کیفیت‌های قابل دانلود پیدا نشد ❌")


async def button(update, context):
    query = update.callback_query
    format_id = query.data
    url = context.user_data.get('video_url')
    await query.answer()

    ydl_opts = {
        'format': f'{format_id}+bestaudio/best',
        'outtmpl': 'video.mp4',
        'merge_output_format': 'mp4'
    }
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
    app.run_polling()

if __name__ == "__main__":
    main()









