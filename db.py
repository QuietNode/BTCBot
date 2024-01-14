import sqlite3


class Database:
    """
    A class used to interact with the database containing facts.

    Attributes:
        con (sqlite3.Connection): Connection to the SQLite database.
        cur (sqlite3.Cursor): Cursor object used to execute SQL commands.
    """

    def __init__(self) -> None:
        """
        Initializes the Database class by connecting to the SQLite database
        and creating the 'facts' table if it does not exist.
        """
        self.__con = sqlite3.connect('database.db')
        self.__cur = self.__con.cursor()

        self.__cur.execute("""CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fact TEXT,
            author TEXT,
            timestamp TEXT
        )""")

    def add_fact(self, fact: str, author: str, timestamp: str) -> None:
        """
        Adds a new fact to the database.

        Parameters:
            fact (str): The fact to be added.
            author (str): The author of the fact.
            timestamp (str): The timestamp when the fact was added.
        """
        self.__cur.execute("INSERT INTO facts (fact, author, timestamp) VALUES (?, ?, ?)", (fact, author, timestamp))
        self.__con.commit()

    def get_facts(self) -> list:
        """
        Retrieves all facts from the database.

        Returns:
            list: A list of tuples containing all facts in the database.
        """
        return self.__cur.execute("SELECT * FROM facts").fetchall()

    def total_facts(self) -> int:
        """
        Counts the total number of facts in the database.

        Returns:
            int: The total number of facts.
        """
        return self.__cur.execute("SELECT COUNT(*) FROM facts").fetchone()[0]

    def get_fact(self, id: int) -> tuple:
        """
        Retrieves a specific fact by its ID.

        Parameters:
            id (int): The ID of the fact to retrieve.

        Returns:
            tuple: A tuple containing the fact with the specified ID.
        """
        fact_list = self.__cur.execute("SELECT * FROM facts WHERE id = ?", (id,)).fetchone()
        if fact_list is None:
            return None, None, None, None
        return self.__cur.execute("SELECT * FROM facts WHERE id = ?", (id,)).fetchone()

    def update_fact(self, id: int, fact: str) -> None:
        """
        Updates the text of an existing fact.

        Parameters:
            id (int): The ID of the fact to update.
            fact (str): The new text of the fact.
        """
        self.__cur.execute("""UPDATE facts SET fact = ? WHERE id = ?""", (fact, id))
        self.__con.commit()
