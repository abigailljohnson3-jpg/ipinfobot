import telebot
import ipinfo
import os
import re
from datetime import datetime

# Get tokens from environment variables (for Railway)
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
IPINFO_TOKEN = os.environ.get('IPINFO_TOKEN', 'YOUR_IPINFO_TOKEN_HERE')

# Initialize bot and IPinfo client
bot = telebot.TeleBot(BOT_TOKEN)
ipinfo_client = ipinfo.getHandler(IPINFO_TOKEN)

# Start command
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
🌍 **IP Information Bot** 🌍

Send me an IP address and I'll give you details about it!

**Commands:**
/start - Show this message
/help - Show this message
/ip <IP> - Get info about a specific IP
/myip - Get info about your own IP

**Examples:**
/ip 8.8.8.8
/myip

Made with ❤️
"""
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

# Handle /myip command
@bot.message_handler(commands=['myip'])
def get_my_ip(message):
    try:
        # Get the user's IP from the message (Telegram doesn't directly provide it)
        # We'll use a fallback - get the IP of the request
        details = ipinfo_client.getDetails()
        response = format_ip_info(details.details)
        bot.reply_to(message, response, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle /ip command
@bot.message_handler(commands=['ip'])
def get_ip_info(message):
    try:
        # Extract IP from command
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Please provide an IP address.\nExample: /ip 8.8.8.8")
            return
        
        ip_address = parts[1]
        
        # Validate IP format (basic check)
        ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        if not ip_pattern.match(ip_address):
            bot.reply_to(message, "❌ Invalid IP address format. Please use IPv4 (e.g., 8.8.8.8)")
            return
        
        # Get IP info
        details = ipinfo_client.getDetails(ip_address)
        response = format_ip_info(details.details)
        bot.reply_to(message, response, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Handle direct IP messages (user just sends an IP)
@bot.message_handler(func=lambda message: True)
def handle_ip_message(message):
    text = message.text.strip()
    
    # Check if message looks like an IP
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    if ip_pattern.match(text):
        try:
            details = ipinfo_client.getDetails(text)
            response = format_ip_info(details.details)
            bot.reply_to(message, response, parse_mode='Markdown')
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")
    else:
        # If not an IP, ignore or send a friendly message
        pass

# Function to format IP info
def format_ip_info(data):
    response = "🔍 **IP Information**\n\n"
    response += f"📌 **IP:** `{data.get('ip', 'N/A')}`\n"
    response += f"🌍 **Location:** {data.get('city', 'N/A')}, {data.get('region', 'N/A')}, {data.get('country', 'N/A')}\n"
    response += f"📍 **Coordinates:** {data.get('loc', 'N/A')}\n"
    response += f"🏢 **ISP:** {data.get('org', 'N/A')}\n"
    response += f"🌐 **Hostname:** {data.get('hostname', 'N/A')}\n"
    response += f"📮 **Postal:** {data.get('postal', 'N/A')}\n"
    response += f"⏰ **Timezone:** {data.get('timezone', 'N/A')}\n"
    return response

# Start polling (for Railway)
if __name__ == "__main__":
    print("🤖 Bot is starting...")
    print(f"Bot username: @{bot.get_me().username}")
    print("✅ Bot is running!")
    bot.infinity_polling()
