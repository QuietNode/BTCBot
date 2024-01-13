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

    def add_fact(self, fact, author, timestamp):
        self.cur.execute("INSERT INTO facts (fact, author, timestamp) VALUES (?, ?, ?)", (fact, author, timestamp))
        self.con.commit()
