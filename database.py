import sqlite3
import logging
from config import DB_NAME

logging.basicConfig(level=logging.INFO)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            lang TEXT DEFAULT 'ar',
            reciter TEXT DEFAULT 'afasy',
            reminder_time TEXT,
            reminder_active INTEGER DEFAULT 0,
            last_activity TIMESTAMP,
            theme TEXT DEFAULT 'light'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sura INTEGER,
            ayah INTEGER,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sura INTEGER,
            ayah INTEGER,
            action TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            user_id INTEGER PRIMARY KEY,
            time TEXT,
            active INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    conn.close()
    logging.info("تم تهيئة قاعدة البيانات بنجاح")

# ----------------- دوال المستخدمين -----------------
def get_user_lang(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row["lang"] if row else "ar"

def set_user_lang(user_id, lang):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, lang) VALUES (?, ?)", (user_id, lang))
    conn.commit()
    conn.close()

def get_user_reciter(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT reciter FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row["reciter"] if row else "afasy"

def set_user_reciter(user_id, reciter):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, reciter) VALUES (?, ?)", (user_id, reciter))
    conn.commit()
    conn.close()

def get_user_theme(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT theme FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row["theme"] if row else "light"

def set_user_theme(user_id, theme):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, theme) VALUES (?, ?)", (user_id, theme))
    conn.commit()
    conn.close()

def set_reminder(user_id, time_str, active=1):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO reminders (user_id, time, active) VALUES (?, ?, ?)",
                   (user_id, time_str, active))
    conn.commit()
    conn.close()

def get_reminder(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT time, active FROM reminders WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return (row["time"], row["active"]) if row else (None, 0)

def delete_reminder(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def add_history(user_id, sura, ayah, action):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (user_id, sura, ayah, action) VALUES (?, ?, ?, ?)",
                   (user_id, sura, ayah, action))
    conn.commit()
    conn.close()

def get_bookmarks(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sura, ayah, note FROM bookmarks WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_bookmark(user_id, sura, ayah, note=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bookmarks (user_id, sura, ayah, note) VALUES (?, ?, ?, ?)",
                   (user_id, sura, ayah, note))
    conn.commit()
    conn.close()

def delete_bookmark(user_id, sura, ayah):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookmarks WHERE user_id = ? AND sura = ? AND ayah = ?",
                   (user_id, sura, ayah))
    conn.commit()
    conn.close()