import sqlite3


class Database:
    def __init__(self):
        self.con = sqlite3.connect('database.db')
        self.cur = self.con.cursor()

        self.cur.execute("""CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fact TEXT,
            author TEXT,
            timestamp TEXT
        )""")

    def add_fact(self, fact: str, author: str , timestamp: str):
        self.cur.execute("INSERT INTO facts (fact, author, timestamp) VALUES (?, ?, ?)", (fact, author, timestamp))
        self.con.commit()

    def get_facts(self):
        return self.cur.execute("SELECT * FROM facts").fetchall()

    def total_facts(self):
        return self.cur.execute("SELECT COUNT(*) FROM facts").fetchone()[0]

    def get_fact(self, id: int):
        return self.cur.execute("SELECT * FROM facts WHERE id = ?", (id,)).fetchone()
