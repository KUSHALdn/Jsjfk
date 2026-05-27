import os
import telebot
import google.generativeai as genai

# Render ke Environment Variables se Tokens uthana
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    print("❌ ERROR: BOT_TOKEN ya GEMINI_API_KEY configuration missing hai!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# AI Model configuration
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

print("🔥 Google AI Bot Render par successfully run ho raha hai... 🚀")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_ai_reply(message):
    chat_type = message.chat.type
    bot_username = bot.get_me().username.lower()
    user_text = message.text
    
    should_reply = False
    
    if chat_type == "private":
        should_reply = True
    elif chat_type in ["group", "supergroup"]:
        if f"@{bot_username}" in user_text.lower():
            user_text = user_text.lower().replace(f"@{bot_username}", "").strip()
            should_reply = True
        elif message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
            should_reply = True

    if should_reply:
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            response = model.generate_content(user_text)
            ai_response = response.text
            bot.reply_to(message, ai_response, parse_mode="Markdown")
        except Exception as e:
            print(f"Error: {e}")
            bot.reply_to(message, "Sorry bhai, abhi dimaag thoda garam hai (Server Error).")

bot.infinity_polling()
