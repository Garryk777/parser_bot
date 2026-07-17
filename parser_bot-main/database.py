import sqlite3
import time

DB_NAME = "subscriptions.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic TEXT,
            expires_at INTEGER,  -- дата окончания (timestamp)
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subscription_id INTEGER,
            keyword TEXT,
            FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
        )
    """)
    conn.commit()
    conn.close()



def get_user_subs(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, topic, expires_at FROM subscriptions WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    result = []
    for sub_id, topic, expires_at in rows:
        cursor.execute("SELECT keyword FROM keywords WHERE subscription_id = ?", (sub_id,))
        keywords = [row[0] for row in cursor.fetchall()]
        days_left = max(0, (expires_at - int(time.time())) // 86400)
        result.append({
            "id": sub_id,
            "topic": topic,
            "keywords": keywords,
            "expires_at": expires_at,
            "days_left": days_left
        })
    conn.close()
    return result


def create_subscription(user_id, topic, days=30):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    expires_at = int(time.time()) + days * 86400  # <-- ЭТА СТРОКА ДОЛЖНА БЫТЬ
    cursor.execute(
        "INSERT INTO subscriptions (user_id, topic, expires_at) VALUES (?, ?, ?)",
        (user_id, topic, expires_at)
    )
    conn.commit()
    conn.close()


def add_keyword(subscription_id, keyword):
    """Добавляет ключевое слово к подписке"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO keywords (subscription_id, keyword) VALUES (?, ?)", (subscription_id, keyword))
    conn.commit()
    conn.close()


def delete_subscription(subscription_id):
    """Удаляет подписку и все её ключевые слова"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM keywords WHERE subscription_id = ?", (subscription_id,))
    cursor.execute("DELETE FROM subscriptions WHERE id = ?", (subscription_id,))
    conn.commit()
    conn.close()


def delete_keyword(subscription_id, keyword):
    """Удаляет конкретное ключевое слово из подписки"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM keywords WHERE subscription_id = ? AND keyword = ?", (subscription_id, keyword))
    conn.commit()
    conn.close()


def update_subscription_topic(sub_id, new_topic):
    """Обновляет тему подписки (без изменения даты)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE subscriptions SET topic = ? WHERE id = ?", (new_topic, sub_id))
    conn.commit()
    conn.close()


def extend_subscription(sub_id, extra_days):
    """Продлевает подписку на указанное количество дней"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE subscriptions SET expires_at = expires_at + ? WHERE id = ?", (extra_days * 86400, sub_id))
    conn.commit()
    conn.close()


def get_all_subscriptions():
    """Возвращает список всех подписок всех пользователей"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT users.user_id, subscriptions.topic, keywords.keyword
        FROM users
        JOIN subscriptions ON users.user_id = subscriptions.user_id
        LEFT JOIN keywords ON subscriptions.id = keywords.subscription_id
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_users_with_subs():
    """Возвращает список всех пользователей с количеством их подписок"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT users.user_id, COUNT(subscriptions.id) as sub_count
        FROM users
        LEFT JOIN subscriptions ON users.user_id = subscriptions.user_id
        GROUP BY users.user_id
        HAVING sub_count > 0
        ORDER BY sub_count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def is_subscription_active(sub_id):
    """Проверяет, активна ли подписка"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT expires_at FROM subscriptions WHERE id = ?", (sub_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False
    return row[0] > int(time.time())


def get_all_users_with_subs_detailed():
    """Возвращает список всех пользователей с их подписками и оставшимися днями"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT users.user_id, subscriptions.id, subscriptions.topic, subscriptions.expires_at
        FROM users
        JOIN subscriptions ON users.user_id = subscriptions.user_id
        ORDER BY users.user_id
    """)
    rows = cursor.fetchall()
    conn.close()

    result = {}
    for user_id, sub_id, topic, expires_at in rows:
        if user_id not in result:
            result[user_id] = []
        days_left = max(0, (expires_at - int(time.time())) // 86400)
        result[user_id].append({
            "sub_id": sub_id,
            "topic": topic,
            "days_left": days_left
        })
    return result