# =========================================
# STANDLEO FACEIT BOT FULL FIX
# Python 3.11+
# pip install pyTelegramBotAPI
# =========================================

import telebot
from telebot import types
import sqlite3
import random
import time
import re

# =========================================
# TOKEN
# =========================================

TOKEN = "8818405158:AAHWwdPc3qLRXjWvO4eOFQf-0L4MSaA80Ow"

bot = telebot.TeleBot(TOKEN)

match_reports = {}   

# =========================================
# SAFE INT
# =========================================

def safe_int(text):

    numbers = re.findall(r'\d+', str(text))

    if not numbers:
        return None

    return int(numbers[0])

# =========================================
# ADMINS
# =========================================

ADMINS = [8663599703]

# =========================================
# DATABASE
# =========================================

conn = sqlite3.connect("standleo.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    nickname TEXT,
    game_id TEXT,
    elo INTEGER DEFAULT 0,
    lvl INTEGER DEFAULT 0,
    calibration INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    loses INTEGER DEFAULT 0,
    kd REAL DEFAULT 1.00,
    warns INTEGER DEFAULT 0,
    mute_until INTEGER DEFAULT 0
)
""")

conn.commit()

# =========================================
# MAPS
# =========================================

MAPS = [
    "Rust",
    "Province",
    "Sandstone",
    "Breeze",
    "Hanami",
    "Prison"
]

# =========================================
# LOBBIES
# =========================================

lobbies = {
    "1x1": [],
    "2x2": [],
    "5x5": []
}

sizes = {
    "1x1": 2,
    "2x2": 4,
    "5x5": 10
}

# =========================================
# PARTIES
# =========================================

parties = {}

# =========================================
# MATCH REPORTS
# =========================================

match_reports = {}

# =========================================
# CREATE USER
# =========================================

def create_user(user_id, username):

    cur.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cur.fetchone()

    if not user:

        cur.execute(
            "INSERT INTO users(user_id, username) VALUES(?, ?)",
            (user_id, username)
        )

        conn.commit()

# =========================================
# GET USER
# =========================================

def get_user(user_id):

    cur.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    return cur.fetchone()

# =========================================
# GET LEVEL
# =========================================

def get_level(elo):

    if elo >= 4000:
        return 10
    elif elo >= 3200:
        return 9
    elif elo >= 2600:
        return 8
    elif elo >= 2200:
        return 7
    elif elo >= 1800:
        return 6
    elif elo >= 1400:
        return 5
    elif elo >= 1000:
        return 4
    elif elo >= 700:
        return 3
    elif elo >= 400:
        return 2
    elif elo >= 200:
        return 1

    return 0

# =========================================
# MAIN MENU
# =========================================

def main_menu():

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("🎮 Играть")
    kb.add("👤 Профиль", "👥 Пати")
    kb.add("🏆 Топ ELO")
    kb.add("⚙ Админ панель")

    return kb

# =========================================
# START
# =========================================

@bot.message_handler(commands=["start"])
def start(message):

    uid = message.from_user.id
    username = message.from_user.username

    create_user(uid, username)

    bot.send_message(
        message.chat.id,
        "🛡 Добро пожаловать в STANDLEO FACEIT\n\n"
        "🎮 Введи ник в игре"
    )

    bot.register_next_step_handler(
        message,
        get_nickname
    )
# =========================
# CALLBACKS
# =========================
@bot.callback_query_handler(func=lambda c: c.data.startswith("result_"))
def send_result(call):
    mode = call.data.split("_", 1)[1]
    msg = bot.send_message(call.message.chat.id, "📸 Отправь скрин")
    bot.register_next_step_handler(msg, process_screenshot, mode)


# =========================
# SCREENSHOT PROCESS
# =========================
def process_screenshot(message, mode):
    if not message.photo:
        bot.send_message(message.chat.id, "❌ Отправь именно фото (скрин)")
        return

    file_id = message.photo[-1].file_id
    report_id = random.randint(1000, 9999)

    match_reports[report_id] = {
        "mode": mode,
        "file_id": file_id,
        "user_id": message.from_user.id
    }

    bot.send_message(
        message.chat.id,
        f"✅ Скрин сохранён!\nID отчёта: {report_id}"
    )
# =========================================
# GET NICKNAME
# =========================================

def get_nickname(message):

    nickname = message.text

    cur.execute(
        "UPDATE users SET nickname=? WHERE user_id=?",
        (nickname, message.from_user.id)
    )

    conn.commit()

    bot.send_message(
        message.chat.id,
        "🆔 Введи ID в игре"
    )

    bot.register_next_step_handler(
        message,
        get_game_id
    )

# =========================================
# GET GAME ID
# =========================================

def get_game_id(message):

    game_id = message.text

    cur.execute(
        "UPDATE users SET game_id=? WHERE user_id=?",
        (game_id, message.from_user.id)
    )

    conn.commit()

    bot.send_message(
        message.chat.id,
        "✅ Регистрация завершена",
        reply_markup=main_menu()
    )

# =========================================
# PROFILE
# =========================================

@bot.message_handler(func=lambda m: m.text == "👤 Профиль")
def profile(message):

    user = get_user(message.from_user.id)

    calibration = user[6]
    elo = user[4]
    lvl = user[5]
    wins = user[7]
    loses = user[8]
    kd = user[9]
    warns = user[10]
    mute_until = user[11]

    total = wins + loses

    if total <= 0:
        wl = 0
    else:
        wl = int((wins / total) * 100)

    if calibration < 5:
        elo_text = "🔒 Calibration"
        lvl_text = "🔒 Calibration"
    else:
        elo_text = f"🔥 {elo}"
        lvl_text = f"{lvl}️⃣"

    mute_text = "Нет"

    if mute_until > int(time.time()):

        remain = mute_until - int(time.time())
        minutes = remain // 60

        mute_text = f"{minutes} мин"

    text = f"""
🛡 STANDLEO FACEIT

👤 Ник: {user[2]}
🆔 Bot ID: {message.from_user.id}
🎮 Игровой ID: {user[3]}
📱 Username: @{user[1]}

ELO: {elo_text}
LVL: {lvl_text}

📊 Калибровка: {calibration}/5

⚔ K/D: {kd}
🏆 W/L: {wl}%

⚠ Варны: {warns}
🔇 Мут: {mute_text}

🔥 Fastuk Faceit
"""

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_menu()
    )

# =========================================
# PLAY MENU
# =========================================

@bot.message_handler(func=lambda m: m.text == "🎮 Играть")
def play_menu(message):

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("1x1", "2x2", "5x5")
    kb.add("🔙 Назад")

    bot.send_message(
        message.chat.id,
        "🎮 Выбери режим",
        reply_markup=kb
    )

# =========================================
# JOIN LOBBY
# =========================================

@bot.message_handler(func=lambda m: m.text in ["1x1", "2x2", "5x5"])
def join_lobby(message):

    uid = message.from_user.id
    mode = message.text

    user = get_user(uid)

    if user[11] > int(time.time()):

        bot.send_message(
            message.chat.id,
            "🔇 У тебя мут"
        )

        return

    if uid not in lobbies[mode]:
        lobbies[mode].append(uid)

    text = f"🛡 Standleo\n"
    text += f"🎮 ЛОББИ {mode}\n\n"

    text += f"Игроков в лобби: {len(lobbies[mode])}/{sizes[mode]}\n\n"

    text += "Игроки в лобби:\n"

    for player in lobbies[mode]:

        u = get_user(player)

        if u[6] < 5:
            text += f"🔒 {u[2]} ({u[6]}/5)\n"
        else:
            text += f"{u[5]}️⃣ {u[2]} (ELO: {u[4]})\n"

    text += "\n🔥 Fastuk Faceit"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("🚪 Выйти из лобби")

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=kb
    )

# =========================================
# EXIT LOBBY
# =========================================

@bot.message_handler(func=lambda m: m.text == "🚪 Выйти из лобби")
def leave_lobby(message):

    uid = message.from_user.id

    for mode in lobbies:

        if uid in lobbies[mode]:
            lobbies[mode].remove(uid)

    bot.send_message(
        message.chat.id,
        "✅ Вы вышли из лобби",
        reply_markup=main_menu()
    )

# =========================================
# PARTY MENU
# =========================================

@bot.message_handler(func=lambda m: m.text == "👥 Пати")
def party_menu(message):

    uid = message.from_user.id

    found = None

    for leader in parties:

        if uid in parties[leader]["members"]:
            found = leader
            break

    if not found:

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

        kb.add("➕ Создать пати")
        kb.add("🔙 Назад")

        bot.send_message(
            message.chat.id,
            "🛡 Standleo\n\n❌ У вас нету пати",
            reply_markup=kb
        )

        return

    show_party(message.chat.id, found, uid)

# =========================================
# CREATE PARTY
# =========================================

@bot.message_handler(func=lambda m: m.text == "➕ Создать пати")
def create_party(message):

    uid = message.from_user.id

    if uid in parties:

        bot.send_message(
            message.chat.id,
            "❌ У тебя уже есть пати"
        )

        return

    parties[uid] = {
        "leader": uid,
        "members": [uid]
    }

    show_party(message.chat.id, uid, uid)

# =========================================
# SHOW PARTY
# =========================================

def show_party(chat_id, leader, viewer):

    party = parties[leader]

    text = "🛡 Standleo\n\n"
    text += "👥 ПАТИ\n\n"

    text += f"👑 Лидер: {get_user(leader)[2]}\n"
    text += f"👥 Состав ({len(party['members'])}/2):\n\n"

    pos = 1

    for uid in party["members"]:

        user = get_user(uid)

        text += f"{pos}. {user[2]}\n"
        text += f"(ID: {uid})\n\n"

        pos += 1

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if viewer == leader:

        kb.add("➕ Добавить игрока")
        kb.add("❌ Кик игрока")

    kb.add("🚪 Выйти из пати")

    bot.send_message(
        chat_id,
        text,
        reply_markup=kb
    )

# =========================================
# ADD PLAYER
# =========================================

@bot.message_handler(func=lambda m: m.text == "➕ Добавить игрока")
def add_player(message):

    leader = message.from_user.id

    msg = bot.send_message(
        message.chat.id,
        "🆔 Введите ID игрока"
    )

    bot.register_next_step_handler(
        msg,
        process_add,
        leader
    )

# =========================================
# PROCESS ADD
# =========================================

def process_add(message, leader):

    target = safe_int(message.text)

    if target is None:

        bot.send_message(
            message.chat.id,
            "❌ Введите только ID"
        )

        return

    if leader not in parties:
        return

    if len(parties[leader]["members"]) >= 2:

        bot.send_message(
            message.chat.id,
            "❌ Пати заполнено"
        )

        return

    parties[leader]["members"].append(target)

    try:

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("🚪 Выйти из пати")

        bot.send_message(
            target,
            "👥 Тебя добавили в пати",
            reply_markup=kb
        )

    except:
        pass

    show_party(message.chat.id, leader, leader)

# =========================================
# KICK PLAYER
# =========================================

@bot.message_handler(func=lambda m: m.text == "❌ Кик игрока")
def kick_player(message):

    leader = message.from_user.id

    msg = bot.send_message(
        message.chat.id,
        "🆔 Введите ID игрока"
    )

    bot.register_next_step_handler(
        msg,
        process_kick,
        leader
    )

# =========================================
# PROCESS KICK
# =========================================

def process_kick(message, leader):

    target = safe_int(message.text)

    if target is None:

        bot.send_message(
            message.chat.id,
            "❌ Введите только ID"
        )

        return

    if leader not in parties:
        return

    if target in parties[leader]["members"]:

        parties[leader]["members"].remove(target)

        try:

            bot.send_message(
                target,
                "❌ Тебя кикнули из пати",
                reply_markup=main_menu()
            )

        except:
            pass

    show_party(message.chat.id, leader, leader)

# =========================================
# LEAVE PARTY
# =========================================

@bot.message_handler(func=lambda m: m.text == "🚪 Выйти из пати")
def leave_party(message):

    uid = message.from_user.id

    for leader in list(parties.keys()):

        if uid in parties[leader]["members"]:

            parties[leader]["members"].remove(uid)

            if len(parties[leader]["members"]) <= 0:
                del parties[leader]

            break

    bot.send_message(
        message.chat.id,
        "✅ Вы вышли из пати",
        reply_markup=main_menu()
    )

# =========================================
# TOP ELO
# =========================================

@bot.message_handler(func=lambda m: m.text == "🏆 Топ ELO")
def top_elo(message):

    cur.execute(
        "SELECT nickname, elo FROM users ORDER BY elo DESC LIMIT 10"
    )

    users = cur.fetchall()

    text = "🏆 ТОП ELO\n\n"

    pos = 1

    for u in users:

        text += f"{pos}. {u[0]} — {u[1]}\n"
        pos += 1

    bot.send_message(message.chat.id, text)


# =========================================
# ADMIN PANEL
# =========================================

@bot.message_handler(func=lambda m: m.text == "⚙ Админ панель")
def admin_panel(message):

    if message.from_user.id not in ADMINS:
        return

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("➕ Выдать ELO")
    kb.add("⭐ Выдать LVL")
    kb.add("⚠ Выдать WARN")
    kb.add("📸 Скрины")
    kb.add("🔙 Назад")

    bot.send_message(
        message.chat.id,
        "⚙ Админ панель",
        reply_markup=kb
    )
# =========================================
# SCREENS MENU
# =========================================

@bot.message_handler(func=lambda m: m.text == "📸 Скрины")
def admin_screens(message):

    if message.from_user.id not in ADMINS:
        return

    if not match_reports:

        bot.send_message(
            message.chat.id,
            "❌ Скринов нет"
        )

        return

    for report_id, data in match_reports.items():

        kb = types.InlineKeyboardMarkup()

        kb.add(
            types.InlineKeyboardButton(
                "✅ Подтвердить матч",
                callback_data=f"approve_{report_id}"
            ),
            types.InlineKeyboardButton(
                "❌ Отменить матч",
                callback_data=f"cancel_{report_id}"
            )
        )

        if "photo" in data:

            bot.send_photo(
                message.chat.id,
                data["photo"],
                caption=f"🛡 MATCH ID: {report_id}",
                reply_markup=kb
            )

        else:

            bot.send_message(
                message.chat.id,
                f"🛡 MATCH ID: {report_id}",
                reply_markup=kb
            )
# =========================================
# GIVE ELO
# =========================================

@bot.message_handler(func=lambda m: m.text == "➕ Выдать ELO")
def give_elo(message):

    if message.from_user.id not in ADMINS:
        return

    msg = bot.send_message(
        message.chat.id,
        "🆔 Введите ID игрока"
    )

    bot.register_next_step_handler(
        msg,
        give_elo_amount
    )

# =========================================
# GIVE ELO AMOUNT
# =========================================

def give_elo_amount(message):

    target = safe_int(message.text)

    if target is None:

        bot.send_message(
            message.chat.id,
            "❌ Только цифры"
        )

        return

    msg = bot.send_message(
        message.chat.id,
        "➕ Сколько ELO?"
    )

    bot.register_next_step_handler(
        msg,
        finish_give_elo,
        target
    )

# =========================================
# FINISH GIVE ELO
# =========================================

def finish_give_elo(message, target):

    amount = safe_int(message.text)

    if amount is None:

        bot.send_message(
            message.chat.id,
            "❌ Только цифры"
        )

        return

    user = get_user(target)

    elo = user[4] + amount
    lvl = get_level(elo)

    cur.execute(
        "UPDATE users SET elo=?, lvl=? WHERE user_id=?",
        (elo, lvl, target)
    )

    conn.commit()

    bot.send_message(
        message.chat.id,
        "✅ ELO выдан"
    )

# =========================================
# BACK
# =========================================

@bot.message_handler(func=lambda m: m.text == "🔙 Назад")
def back(message):

    bot.send_message(
        message.chat.id,
        "🏠 Главное меню",
        reply_markup=main_menu()
    )

# =========================================
# RUN
# =========================================

bot.remove_webhook()

print("BOT STARTED")

bot.infinity_polling(skip_pending=True)
