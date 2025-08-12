import sqlite3

def init_db():
    conn = sqlite3.connect('osu_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            osu_username TEXT,
            osu_user_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    print("[!] database initialization was successful.")


def save_user_profile(user_id, osu_username, osu_user_id):
    conn = sqlite3.connect('osu_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, osu_username, osu_user_id)
        VALUES (?, ?, ?)
    ''', (user_id, osu_username, osu_user_id))
    conn.commit()
    conn.close()

def get_user_profile(user_id):
    conn = sqlite3.connect('osu_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT osu_username, osu_user_id FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def delete_user_profile(user_id):
    conn = sqlite3.connect('osu_bot.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    rowcount = cursor.rowcount
    conn.commit()
    conn.close()
    return rowcount > 0