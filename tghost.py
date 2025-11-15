import os
import subprocess
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8088567498:AAG56QUsy18uf0aqjI6uzmLASDCgKEPhfgE"
BASE_DIR = "user_bots"
os.makedirs(BASE_DIR, exist_ok=True)

running_bots = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Welcome to Jalwa Hosting Bot v20!*\n\n"
        "📤 Send your `.py` bot file to host it.\n\n"
        "Commands:\n"
        "▶️ /startbot - Start your uploaded bot\n"
        "⏹ /stopbot - Stop running bot\n"
        "📜 /logs - View latest logs",
        parse_mode="Markdown"
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_dir = os.path.join(BASE_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)

    doc = update.message.document
    file_path = os.path.join(user_dir, doc.file_name)
    file = await doc.get_file()
    await file.download_to_drive(file_path)
    context.user_data["filename"] = doc.file_name

    await update.message.reply_text(f"✅ File `{doc.file_name}` uploaded!\nUse /startbot to run it.", parse_mode="Markdown")

async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_dir = os.path.join(BASE_DIR, user_id)
    filename = context.user_data.get("filename")

    if not filename:
        await update.message.reply_text("⚠️ Upload a `.py` file first.")
        return

    file_path = os.path.join(user_dir, filename)
    log_path = os.path.join(user_dir, "bot_log.txt")

    proc = subprocess.Popen(["python3", file_path],
                            stdout=open(log_path, "a"),
                            stderr=subprocess.STDOUT)
    running_bots[user_id] = {"pid": proc.pid, "file": filename}
    await update.message.reply_text(f"🚀 `{filename}` started!\nPID: {proc.pid}", parse_mode="Markdown")

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in running_bots:
        await update.message.reply_text("⚠️ No running bot found.")
        return
    pid = running_bots[user_id]["pid"]
    os.system(f"kill {pid}")
    del running_bots[user_id]
    await update.message.reply_text("⏹ Bot stopped successfully.")

async def show_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    log_path = os.path.join(BASE_DIR, user_id, "bot_log.txt")
    if not os.path.exists(log_path):
        await update.message.reply_text("⚠️ No logs yet.")
        return
    with open(log_path) as f:
        lines = f.readlines()[-30:]
    text = "".join(lines)[-4000:]
    await update.message.reply_text("📜 *Last 30 Log Lines:*\n\n" + text, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("startbot", start_bot))
    app.add_handler(CommandHandler("stopbot", stop_bot))
    app.add_handler(CommandHandler("logs", show_logs))
    app.add_handler(MessageHandler(filters.Document.MimeType("text/x-python"), handle_file))

    print("🤖 Jalwa Host Bot v20 is running...")
    app.run_polling()

if __name__ == "__main__":
    main()