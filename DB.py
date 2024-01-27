import sqlite3


class DbConnect:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def connect(self):
        with sqlite3.connect('YouTube.db') as db:
            cursor = db.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS media(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_tg INTEGER UNIQUE,
            url TEXT
            )""")
            db.commit()
            cursor.execute(f"INSERT OR IGNORE INTO media (id_tg) VALUES ({self.chat_id})")
            db.commit()

    def add_url(self, name_video):
        with sqlite3.connect('YouTube.db') as db:
            cursor = db.cursor()
            cursor.execute(f"UPDATE media SET url = '{name_video}' WHERE id_tg = {self.chat_id}")
            db.commit()

    def get_url(self):
        with sqlite3.connect('YouTube.db') as db:
            cursor = db.cursor()
            cursor.execute(f"SELECT url FROM media WHERE id_tg = {self.chat_id}")
            url = cursor.fetchone()[0]
        return url
