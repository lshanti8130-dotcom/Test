import telebot
import psutil
import platform
import requests
import random
from datetime import datetime

TOKEN = '7657850524:AAEKV1lZpTcbqreAhRVnMiIbUGZhdwaqgAI'
bot = telebot.TeleBot(TOKEN)

# 1. Start / Help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome = "🤖 Bot is alive in " + ("a Group!" if message.chat.type != 'private' else "Private Chat!")
    bot.reply_to(message, f"{welcome}\nCommands: /status, /sysinfo, /btc, /game")

# 2. Status (Works in Groups)
@bot.message_handler(commands=['status'])
def report_status(message):
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    bot.reply_to(message, f"📊 *Group Status:*\n🖥 CPU: {cpu}%\n💾 RAM: {ram}%", parse_mode='Markdown')

# 3. SysInfo (Fixed for Groups)
@bot.message_handler(commands=['sysinfo'])
def sys_info(message):
    info = f"📝 *Server:* {platform.node()}\n🏠 *Chat ID:* `{message.chat.id}`"
    bot.reply_to(message, info, parse_mode='Markdown')

# 4. Bitcoin Price
@bot.message_handler(commands=['btc'])
def get_btc(message):
    try:
        data = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()
        price = float(data['price'])
        bot.reply_to(message, f"₿ Bitcoin: `${price:,.2f}`")
    except:
        bot.reply_to(message, "⚠️ Price service down.")

# 5. Echo / Hello (Catches group text)
@bot.message_handler(func=lambda m: True)
def group_echo(message):
    if "hello bot" in message.text.lower():
        bot.reply_to(message, "👋 Hello everyone in the group!")
    
    # Optional: Log group messages to your VPS terminal
    if message.chat.type != 'private':
        print(f"[{message.chat.title}] {message.from_user.first_name}: {message.text}")

print("Bot is starting for Groups...")
bot.infinity_polling()
