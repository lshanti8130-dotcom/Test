import telebot
import psutil
import platform
from datetime import datetime

# Replace with your actual token from BotFather
TOKEN = '7657850524:AAEKV1lZpTcbqreAhRVnMiIbUGZhdwaqgAI'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🤖 *VPS Watchdog Active!*\n\n"
        "Commands:\n"
        "/status - Check CPU, RAM, and Uptime\n"
        "/sysinfo - Get OS details\n"
        "Anything else - I'll echo it back!"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def report_status(message):
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    
    status_msg = (
        f"📊 *Current Status:*\n"
        f"🖥 CPU Usage: {cpu}%\n"
        f"💾 RAM Usage: {ram}%\n"
        f"🕒 Booted since: {boot_time}"
    )
    bot.reply_to(message, status_msg, parse_mode='Markdown')

@bot.message_handler(commands=['sysinfo'])
def sys_info(message):
    info = (
        f"📝 *System Info:*\n"
        f"OS: {platform.system()} {platform.release()}\n"
        f"Node: {platform.node()}\n"
        f"Arch: {platform.machine()}"
    )
    bot.reply_to(message, info, parse_mode='Markdown')

# Echo everything else
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"You said: {message.text}")

print("Bot is running...")
bot.infinity_polling()
