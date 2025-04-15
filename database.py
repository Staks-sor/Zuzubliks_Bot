import sqlite3

class Database:
    def __init__(self, db_path="zuzubliks.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    xpath TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_site(self, title, url, xpath):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sites (title, url, xpath) VALUES (?, ?, ?)",
                (title, url, xpath)
            )
            conn.commit()

    def get_all_sites(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, url, xpath FROM sites")
            return cursor.fetchall()