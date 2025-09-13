import telebot

BOT_TOKEN = "8372914316:AAFYI6nE5fRckNJdyAfXNeerAp2hxbpV_rY"  # <-- paste your bot token here
bot = telebot.TeleBot(BOT_TOKEN)

updates = bot.get_updates()
for u in updates:
    print(f"Name: {u.message.from_user.first_name}, Chat ID: {u.message.chat.id}")
