import aiosqlite
from datetime import datetime

DB_NAME = "finance.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            type TEXT,
            date TEXT
        )
        """)
        await db.commit()


async def add_transaction(user_id, amount, category, type_):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO transactions (user_id, amount, category, type, date)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, amount, category, type_, datetime.now().isoformat()))
        await db.commit()


async def get_month_stats(user_id):
    now = datetime.now().strftime("%Y-%m")

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT type, SUM(amount)
        FROM transactions
        WHERE user_id = ? AND date LIKE ?
        GROUP BY type
        """, (user_id, f"{now}%"))

        rows = await cursor.fetchall()

    result = {"income": 0, "expense": 0}
    for row in rows:
        result[row[0]] = row[1] or 0

    return result