import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'database.db')


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()

        # Создаем таблицу для заказов
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tariff TEXT,
                status TEXT
            )
        ''')
        self.conn.commit()

    def insert_order(self, user_id, tariff, status):
        self.cur.execute('INSERT INTO orders (user_id, tariff, status) VALUES (?, ?, ?)', (user_id, tariff, status))
        self.conn.commit()

    def get_order_status(self, user_id):
        self.cur.execute('SELECT status FROM orders WHERE user_id=?', (user_id,))
        row = self.cur.fetchone()
        if row:
            return row[0]
        return None

    def update_order_status(self, user_id, new_status):
        self.cur.execute('UPDATE orders SET status=? WHERE user_id=?', (new_status, user_id))
        self.conn.commit()

    def close(self):
        self.conn.close()
