import telebot
import ipinfo
import os
import re

# Get tokens from environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
IPINFO_TOKEN = os.environ.get('IPINFO_TOKEN')

# Check if tokens exist
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN environment variable not set!")
    exit(1)

if not IPINFO_TOKEN:
    print("❌ ERROR: IPINFO_TOKEN environment variable not set!")
    exit(1)

# Initialize bot and IPinfo client
bot = telebot.TeleBot(BOT_TOKEN)
ipinfo_client = ipinfo.getHandler(IPINFO_TOKEN)

# Start command
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
🌍 IP Information Bot 🌍

Send me an IP address and I'll give you details about it!

Commands:
/start - Show this message
/help - Show this message
/ip <IP> - Get info about a specific IP
/myip - Get info about your own IP

Examples:
/ip 8.8.8.8
/myip

Made with ❤️
"""
    bot.reply_to(message, welcome_text)

# Handle /myip command
@bot.message_handler(commands=['myip'])
def get_my_ip(message):
    try:
        details = ipinfo_client.getDetails()
        response = format_ip_info(details.details)
        bot.reply_to(message, response, parse_mode='MarkdownV2')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle /ip command
@bot.message_handler(commands=['ip'])
def get_ip_info(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Please provide an IP address.\nExample: /ip 8.8.8.8")
            return
        
        ip_address = parts[1]
        
        ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        if not ip_pattern.match(ip_address):
            bot.reply_to(message, "❌ Invalid IP address format. Please use IPv4 (e.g., 8.8.8.8)")
            return
        
        details = ipinfo_client.getDetails(ip_address)
        response = format_ip_info(details.details)
        bot.reply_to(message, response, parse_mode='MarkdownV2')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle direct IP messages
@bot.message_handler(func=lambda message: True)
def handle_ip_message(message):
    text = message.text.strip()
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    if ip_pattern.match(text):
        try:
            details = ipinfo_client.getDetails(text)
            response = format_ip_info(details.details)
            bot.reply_to(message, response, parse_mode='MarkdownV2')
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")

# Function to format IP info with proper MarkdownV2 escaping
def format_ip_info(data):
    # Helper function to escape special characters for MarkdownV2
    def escape_markdown(text):
        if text is None:
            return "N/A"
        # Escape special characters: _ * [ ] ( ) ~ ` > # + - = | { } . !
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    ip = escape_markdown(data.get('ip', 'N/A'))
    city = escape_markdown(data.get('city', 'N/A'))
    region = escape_markdown(data.get('region', 'N/A'))
    country = escape_markdown(data.get('country', 'N/A'))
    loc = escape_markdown(data.get('loc', 'N/A'))
    org = escape_markdown(data.get('org', 'N/A'))
    hostname = escape_markdown(data.get('hostname', 'N/A'))
    postal = escape_markdown(data.get('postal', 'N/A'))
    timezone = escape_markdown(data.get('timezone', 'N/A'))
    
    response = (
        f"🔍 **IP Information**\n\n"
        f"📌 **IP:** `{ip}`\n"
        f"🌍 **Location:** {city}, {region}, {country}\n"
        f"📍 **Coordinates:** {loc}\n"
        f"🏢 **ISP:** {org}\n"
        f"🌐 **Hostname:** {hostname}\n"
        f"📮 **Postal:** {postal}\n"
        f"⏰ **Timezone:** {timezone}"
    )
    return response

# Start polling
if __name__ == "__main__":
    print("🤖 IP Bot is starting...")
    try:
        bot_info = bot.get_me()
        print(f"✅ Bot is running! Username: @{bot_info.username}")
    except Exception as e:
        print(f"⚠️ Could not get bot info: {e}")
        print("Check your BOT_TOKEN.")
    bot.infinity_polling()
